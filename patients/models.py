from django.db import models

class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    def __str__(self):
        return self.name

class Diagnostic(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    cbc = models.JSONField(default=dict)
    calcium = models.FloatField(null=True, blank=True)
    creatinine = models.FloatField(null=True, blank=True)
    beta2_microglobulin = models.FloatField(null=True, blank=True)
    ldh = models.FloatField(null=True, blank=True)
    imaging_results = models.JSONField(default=dict)
    biomarkers = models.JSONField(default=dict)
    date = models.DateField(auto_now_add=True)

class Monitoring(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    m_protein = models.FloatField(null=True, blank=True)
    mrD_status = models.CharField(max_length=50)
    symptoms = models.JSONField(default=list)
