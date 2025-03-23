from django.urls import path
from . import views

urlpatterns = [
    path('<str:patient_id>/diagnostics', views.submit_diagnostics),
    path('<str:patient_id>/next-tests', views.next_tests),
    path('<str:patient_id>/staging', views.staging),
    path('<str:patient_id>/treatment-recommendations', views.treatment_recommendations),
    path('<str:patient_id>/monitoring', views.submit_monitoring),
]
