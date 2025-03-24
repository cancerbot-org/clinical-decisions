from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Patient, Diagnostic, Monitoring
import json



@csrf_exempt
@require_http_methods(["POST"])
def submit_diagnostics(request, patient_id):
    data = json.loads(request.body)
    try:
        patient = Patient.objects.get(patient_id=patient_id).first()
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    Diagnostic.objects.create(
        patient=patient,
        cbc=data.get('labResults', {}).get('cbc', {}),
        calcium=data.get('labResults', {}).get('calcium'),
        creatinine=data.get('labResults', {}).get('creatinine'),
        beta2_microglobulin=data.get('labResults', {}).get('beta2Microglobulin'),
        ldh=data.get('labResults', {}).get('ldh'),
        imaging_results=data.get('imagingResults', {}),
        biomarkers=data.get('biomarkers', {})
    )

    return JsonResponse({
        'message': 'Diagnostics uploaded successfully.',
        'nextStep': f'/patients/{patient_id}/next-tests'
    })

@require_http_methods(["GET"])
def next_tests(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        latest_diag = Diagnostic.objects.filter(patient=patient).latest('date')
    except (Patient.DoesNotExist, Diagnostic.DoesNotExist):
        return JsonResponse({'error': 'Patient or diagnostics not found'}, status=404)

    recommended_tests = []
    rationale = []

    if not latest_diag.biomarkers.get('cytogenetics'):
        recommended_tests.append("FISH for t(4;14) and t(14;16)")
        rationale.append("High-risk cytogenetics not fully assessed.")

    if latest_diag.beta2_microglobulin and latest_diag.beta2_microglobulin > 5.5:
        recommended_tests.append("Bone Marrow Biopsy")
        rationale.append("Elevated beta-2 microglobulin requires marrow confirmation.")

    return JsonResponse({'patientId': patient_id,'nextRecommendedTests': recommended_tests,'rationale': rationale})

@require_http_methods(["GET"])
def staging(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        latest_diag = Diagnostic.objects.filter(patient=patient).latest('date')
    except (Patient.DoesNotExist, Diagnostic.DoesNotExist):
        return JsonResponse({'error': 'Patient or diagnostics not found'}, status=404)

    iss_stage = "Stage I"
    rIss_stage = "Stage I"
    prognosis = "Standard risk disease"

    if latest_diag.beta2_microglobulin > 5.5:
        iss_stage = "Stage III"

    if latest_diag.ldh and latest_diag.ldh > 250:
        rIss_stage = "Stage III"
        prognosis = "High-risk disease with poor prognosis"

    if "del(17p)" in latest_diag.biomarkers.get('cytogenetics', []):
        prognosis = "High-risk disease due to cytogenetics"

    return JsonResponse({
        'patientId': patient_id,
        'issStage': iss_stage,
        'rIssStage': rIss_stage,
        'prognosis': prognosis
    })

@require_http_methods(["GET"])
def treatment_recommendations(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        latest_diag = Diagnostic.objects.filter(patient=patient).latest('date')
    except (Patient.DoesNotExist, Diagnostic.DoesNotExist):
        return JsonResponse({'error': 'Patient or diagnostics not found'}, status=404)

    recommendations = []
    notes = []

    # 1️⃣ Performance status and eligibility for aggressive therapy
    if patient.ecog_performance_status is not None and patient.ecog_performance_status <= 2:
        recommendations.append("Eligible for aggressive treatment options (VRd, KRd).")
    elif patient.karnofsky_performance_score is not None and patient.karnofsky_performance_score >= 70:
        recommendations.append("Consider standard induction therapy with lenalidomide-based regimens.")
    else:
        recommendations.append("Consider less intensive therapy (Rd-lite, DRd).")

    # 2️⃣ Stem cell transplant eligibility
    if not patient.stem_cell_transplant_history:
        recommendations.append("Eligible for Autologous Stem Cell Transplant (ASCT). Collect stem cells.")
    else:
        notes.append("Stem cell transplant already performed.")

    # 3️⃣ Cytogenetic high-risk markers (assume csv contains markers)
    high_risk_markers = ["del17p", "t(4;14)", "t(14;16)"]
    if patient.cytogenic_markers:
        markers = [m.strip().lower() for m in patient.cytogenic_markers.split(',')]
        if any(marker in markers for marker in high_risk_markers):
            recommendations.append("High-risk cytogenetics: consider quadruplet regimens (Dara-KRd).")
        else:
            notes.append("Standard-risk cytogenetics detected.")

    # 4️⃣ CRAB criteria or SLiM-CRAB (disease-defining events)
    if patient.meets_crab or patient.meets_slim:
        recommendations.append("Initiate systemic therapy per IMWG criteria (meets SLiM-CRAB).")
    else:
        recommendations.append("Consider observation or clinical trial enrollment.")

    # 5️⃣ Peripheral neuropathy considerations
    if patient.peripheral_neuropathy_grade and patient.peripheral_neuropathy_grade >= 2:
        recommendations.append("Avoid bortezomib; consider carfilzomib or ixazomib instead.")

    # 6️⃣ Renal impairment (adjust treatment)
    if patient.serum_creatinine_level and patient.serum_creatinine_level > 2.0:
        recommendations.append("Renal impairment detected: dose-adjust lenalidomide and avoid nephrotoxic agents.")

    # 7️⃣ Previous therapy refractory status
    if patient.treatment_refractory_status:
        notes.append(f"Refractory to: {patient.treatment_refractory_status}. Consider next-line salvage regimens (DPd, IsaPd, Selinexor combinations).")

    # 8️⃣ Progression noted
    if patient.progression and "progression" in patient.progression.lower():
        recommendations.append("Disease progression detected: initiate relapse/refractory regimen.")

    # 9️⃣ Frailty assessment (simplified)
    if patient.karnofsky_performance_score and patient.karnofsky_performance_score < 60:
        recommendations.append("Consider frailty-adapted treatment: low-dose dexamethasone, avoid triplet regimens.")

    # Example of default fallback recommendation
    if not recommendations:
        recommendations.append("No immediate treatment recommendation. Recommend multidisciplinary board discussion.")

    # 10️⃣ Summary response
    response = {
        'patient_id': patient_id,
        'recommendations': recommendations,
        'notes': notes,
        'nextStep': 'Schedule follow-up consultation in 4 weeks or sooner based on lab results.'
    }

    return JsonResponse(response, status=200)

@csrf_exempt
@require_http_methods(["POST"])
def submit_monitoring(request, patient_id):
    data = json.loads(request.body)
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    Monitoring.objects.create(
        patient=patient,
        date=data.get('date'),
        m_protein=data.get('mProtein'),
        mrD_status=data.get('mrDStatus'),
        symptoms=data.get('symptoms', [])
    )

    return JsonResponse({
        'message': 'Monitoring data uploaded.',
        'recommendation': 'Continue maintenance therapy. Next assessment in 3 months.'
    })