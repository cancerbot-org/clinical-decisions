
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["POST"])
def submit_diagnostics(request, patient_id):
    # your function logic here
    return JsonResponse({'message': 'Diagnostics submitted'})

@require_http_methods(["GET"])
def next_tests(request, patient_id):
    return JsonResponse({'message': 'Next tests'})

@require_http_methods(["GET"])
def staging(request, patient_id):
    return JsonResponse({'message': 'Staging'})

@require_http_methods(["GET"])
def treatment_recommendations(request, patient_id):
    return JsonResponse({'message': 'Treatment recommendations'})

@csrf_exempt
@require_http_methods(["POST"])
def submit_monitoring(request, patient_id):
    return JsonResponse({'message': 'Monitoring submitted'})