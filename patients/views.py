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
    supportive_care = []

    if "del(17p)" in latest_diag.biomarkers.get('cytogenetics', []):
        recommendations.append({
            'lineOfTherapy': 'First-line',
            'recommendation': 'Daratumumab + VRd + ASCT (if eligible)',
            'rationale': 'High-risk cytogenetics present'
        })
    else:
        recommendations.append({
            'lineOfTherapy': 'First-line',
            'recommendation': 'VRd induction therapy followed by ASCT (if eligible)',
            'rationale': 'Standard-risk disease'
        })

    supportive_care.append("Bisphosphonates for bone lesions")

    return JsonResponse({
        'patientId': patient_id,
        'treatmentRecommendations': recommendations,
        'supportiveCare': supportive_care
    })

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