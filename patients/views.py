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
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    try:
        # Retrieve or create the patient by patient_id
        patient, created = Patient.objects.get_or_create(patient_id=patient_id)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found'}, status=404)

    # Update fields with incoming data
    patient.karnofsky_performance_score = data.get('karnofsky_performance_score')
    patient.ecog_performance_status = data.get('ecog_performance_status')
    patient.stem_cell_transplant_history = data.get('stem_cell_transplant_history')
    patient.cytogenic_markers = data.get('cytogenic_markers')
    patient.peripheral_neuropathy_grade = data.get('peripheral_neuropathy_grade')

    patient.serum_creatinine_level = data.get('serum_creatinine_level')
    patient.creatinine_clearance_rate = data.get('creatinine_clearance_rate')
    patient.serum_calcium_level = data.get('serum_calcium_level')
    patient.hemoglobin_level = data.get('hemoglobin_level')

    patient.bone_lesions = data.get('bone_lesions')
    patient.bone_imaging_result = data.get('bone_imaging_result')

    patient.clonal_bone_marrow_plasma_cells_percentage = data.get('clonal_bone_marrow_plasma_cells_percentage')
    patient.kappa_flc = data.get('kappa_flc')
    patient.lambda_flc = data.get('lambda_flc')

    patient.treatment_refractory_status = data.get('treatment_refractory_status')
    patient.progression = data.get('progression')

    patient.beta2_microglobulin = data.get('beta2_microglobulin')
    patient.albumin = data.get('albumin')
    patient.lactate_dehydrogenase_level = data.get('lactate_dehydrogenase_level')

    # --------
    # Compute meets_crab
    # --------
    meets_crab = False
    crab_criteria = {
        'C': patient.serum_calcium_level is not None and patient.serum_calcium_level > 11,
        'R': (
            (patient.serum_creatinine_level is not None and patient.serum_creatinine_level > 2) or
            (patient.creatinine_clearance_rate is not None and patient.creatinine_clearance_rate < 40)
        ),
        'A': patient.hemoglobin_level is not None and patient.hemoglobin_level < 10,
        'B': patient.bone_lesions is not None and str(patient.bone_lesions).lower() not in ['0', 'none']
    }

    # If ANY CRAB criterion is met, set meets_crab = True
    meets_crab = any(crab_criteria.values())
    patient.meets_crab = meets_crab

    # --------
    # Compute meets_slim
    # --------
    meets_slim = False
    slim_criteria = {
        'S': patient.clonal_bone_marrow_plasma_cells_percentage is not None and patient.clonal_bone_marrow_plasma_cells_percentage >= 60,
        'Li': (
            patient.kappa_flc is not None and patient.lambda_flc is not None and
            (
                (patient.kappa_flc / max(patient.lambda_flc, 1)) >= 100 or
                (patient.lambda_flc / max(patient.kappa_flc, 1)) >= 100
            )
        ),
        'M': (
            patient.bone_imaging_result is not None and patient.bone_imaging_result.lower() == 'yes' and
            patient.bone_lesions is not None and (
                str(patient.bone_lesions) in ['2', 'more than 2']
            )
        )
    }

    # If ANY SLiM criterion is met, set meets_slim = True
    meets_slim = any(slim_criteria.values())
    patient.meets_slim = meets_slim

    # Save the patient record
    patient.save()

    return JsonResponse({
        'message': 'Patient diagnostics successfully updated.',
        'patient_id': patient.patient_id,
        'meets_crab': meets_crab,
        'meets_slim': meets_slim,
        'crab_criteria': crab_criteria,
        'slim_criteria': slim_criteria
    }, status=200)

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

    framework = request.GET.get("framework", "").lower()
    # Convert framework to lowercase safely
    framework = (framework or "").lower()

    # === ✅ NICE FRAMEWORK PATH ===
    if framework == "nice":
        # 1️⃣ Fit vs frail
        if patient.karnofsky_performance_score and patient.karnofsky_performance_score >= 70:
            recommendations.append("NICE: Fit for intensive treatment → Offer bortezomib + thalidomide + dexamethasone (VTD).")
        else:
            recommendations.append("NICE: Frail or transplant-ineligible → Offer lenalidomide + dexamethasone (Rd) or VMP if fit enough.")

        # 2️⃣ Stem cell transplant
        if not patient.stem_cell_transplant_history:
            if patient.karnofsky_performance_score and patient.karnofsky_performance_score >= 70:
                recommendations.append("NICE: Consider autologous stem cell transplant following induction with VTD.")
            else:
                notes.append("Not eligible for stem cell transplant under NICE criteria.")
        else:
            notes.append("Stem cell transplant already performed.")

        # 3️⃣ Disease activity
        if patient.meets_crab or patient.meets_slim:
            recommendations.append("NICE: Meets SLiM-CRAB criteria → Initiate systemic therapy.")

        # 4️⃣ Relapsed/Refractory
        if patient.treatment_refractory_status or (patient.progression and "progression" in patient.progression.lower()):
            recommendations.append("NICE: Relapse → Offer daratumumab + lenalidomide + dexamethasone (DRd), or carfilzomib-based regimen if previously treated.")

        # 5️⃣ Renal Impairment
        if patient.serum_creatinine_level and patient.serum_creatinine_level > 2.0:
            recommendations.append("NICE: Renal impairment → Consider bortezomib-based treatment (VCD or VMP). Dose-adjust lenalidomide.")

        # 6️⃣ Cytogenetics
        high_risk_markers = ["del17p", "t(4;14)", "t(14;16)"]
        if patient.cytogenic_markers:
            markers = [m.strip().lower() for m in patient.cytogenic_markers.split(',')]
            if any(marker in markers for marker in high_risk_markers):
                recommendations.append("NICE: High-risk cytogenetics → Consider clinical trial or more aggressive triplet/quadruplet regimen.")

        # 7️⃣ Peripheral neuropathy
        if patient.peripheral_neuropathy_grade and patient.peripheral_neuropathy_grade >= 2:
            recommendations.append("NICE: Avoid thalidomide and bortezomib due to neuropathy — consider lenalidomide-based regimens.")

        # Default note
        if not recommendations:
            recommendations.append("NICE: No specific recommendation found — refer to haematology MDT.")

    # === ✅ DEFAULT LOGIC from consensus practice and literature ===
    else:
        if patient.ecog_performance_status is not None and patient.ecog_performance_status <= 2:
            recommendations.append("Eligible for aggressive treatment options (VRd, KRd).")
        elif patient.karnofsky_performance_score is not None and patient.karnofsky_performance_score >= 70:
            recommendations.append("Consider standard induction therapy with lenalidomide-based regimens.")
        else:
            recommendations.append("Consider less intensive therapy (Rd-lite, DRd).")

        if not patient.stem_cell_transplant_history:
            transplant_eligible = (
                (patient.karnofsky_performance_score and patient.karnofsky_performance_score >= 70) or
                (patient.ecog_performance_status and patient.ecog_performance_status <= 2)
            )
            if transplant_eligible:
                recommendations.append("Transplant Eligible → Induction therapy with Daratumumab + VRd (preferred).")
            else:
                recommendations.append("Transplant Ineligible → Consider DRd or lenalidomide + dexamethasone (Rd).")
        else:
            notes.append("Stem cell transplant already performed.")

        high_risk_markers = ["del17p", "t(4;14)", "t(14;16)"]
        if patient.cytogenic_markers:
            markers = [m.strip().lower() for m in patient.cytogenic_markers.split(',')]
            if any(marker in markers for marker in high_risk_markers):
                recommendations.append("High-risk cytogenetics: consider quadruplet regimens (Dara-KRd).")
            else:
                notes.append("Standard-risk cytogenetics detected.")

        if patient.meets_crab or patient.meets_slim:
            recommendations.append("Initiate systemic therapy per IMWG criteria (meets SLiM-CRAB).")
        else:
            recommendations.append("Consider observation or clinical trial enrollment.")

        if patient.peripheral_neuropathy_grade and patient.peripheral_neuropathy_grade >= 2:
            recommendations.append("Avoid bortezomib; consider carfilzomib or ixazomib instead.")

        if patient.serum_creatinine_level and patient.serum_creatinine_level > 2.0:
            recommendations.append("Renal impairment detected: dose-adjust lenalidomide and avoid nephrotoxic agents.")

        if patient.treatment_refractory_status:
            notes.append(f"Refractory to: {patient.treatment_refractory_status}. Consider next-line salvage regimens (DPd, IsaPd, Selinexor combinations).")

        if patient.progression and "progression" in patient.progression.lower():
            recommendations.append("Disease progression detected: initiate relapse/refractory regimen.")

        if patient.karnofsky_performance_score and patient.karnofsky_performance_score < 60:
            recommendations.append("Consider frailty-adapted treatment: low-dose dexamethasone, avoid triplet regimens.")

        if not recommendations:
            recommendations.append("No immediate treatment recommendation. Recommend multidisciplinary board discussion.")

    # Final response
    response = {
        'patient_id': patient_id,
        'framework': framework.upper() if framework else "CONSENSUS",
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