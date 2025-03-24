from django.db import models


class GenderChoices(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    UNKNOWN = 'UN', 'Unknown'
    EMPTY = '', 'Empty'


class WeightUnits(models.TextChoices):
    KG = 'kg', 'Kilograms'
    LB = 'lb', 'Pounds'


class HeightUnits(models.TextChoices):
    CM = 'cm', 'Centimeters'
    M = 'm', 'Meters'
    FT = 'ft', 'Feet'
    IN = 'in', 'Inches'


class HemoglobinUnits(models.TextChoices):
    G_DL = 'G/DL', 'g/deciliter'
    G_L = 'G/L', 'g/Liter'


class PlateletCountUnits(models.TextChoices):
    CELLS_UL = 'CELLS/UL', 'cells/microliter'
    CELLS_L = 'CELLS/L', 'cells/Liter'


class SerumCreatinineUnits(models.TextChoices):
    MG_DL = 'MG/DL', 'mg/dL'
    MICROMOLES_L = 'MICROMOLES/L', 'micromoles/L'


class SerumBilirubinUnits(models.TextChoices):
    MG_DL = 'MG/DL', 'mg/dL'
    MICROMOLES_L = 'MICROMOLES/L', 'micromoles/L'


class SerumCalciumUnits(models.TextChoices):
    MG_DL = 'MG/DL', 'mg/dL'
    MICROMOLES_L = 'MICROMOLES/L', 'micromoles/L'


class Patient(models.Model):
    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()

    # -------------
    # Disease block
    # -------------

    # no need for patient_age with date_of_birth
    # patient_age = models.IntegerField(help_text="What is the patient's age?", blank=True, null=True)
    gender = models.CharField(
        max_length=2,
        choices=GenderChoices.choices,
        blank=True,
        null=True,
        help_text="What is the patient's gender (leave empty if there is no requirement)?"
    )
    weight = models.FloatField(help_text="Patient's weight", blank=True, null=True)
    weight_units = models.CharField(
        max_length=2,
        choices=WeightUnits.choices,
        blank=True,
        null=True,
        default='kg',
        help_text="Units for the patient's weight"
    )
    height = models.FloatField(help_text="Patient's height", blank=True, null=True)
    height_units = models.CharField(
        max_length=2,
        choices=HeightUnits.choices,
        blank=True,
        null=True,
        default='cm',
        help_text="Units for the patient's height"
    )
    bmi = models.FloatField(editable=False, help_text="Patient's BMI (computed)", blank=True, null=True)
    ethnicity = models.TextField(blank=True, null=True)  # enum
    systolic_blood_pressure = models.IntegerField(help_text="Patient's systolic blood pressure", blank=True, null=True)
    diastolic_blood_pressure = models.IntegerField(help_text="Patient's diastolic blood pressure", blank=True, null=True)

    # Location
    country = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    # geo_point = PointField(blank=True, null=True, srid=4326)  TODO: can be added later

    disease = models.TextField(blank=True, null=True, default='multiple myeloma')
    stage = models.TextField(blank=True, null=True)
    karnofsky_performance_score = models.IntegerField(blank=True, null=True, default=100)
    ecog_performance_status = models.IntegerField(blank=True, null=True)
    no_other_active_malignancies = models.BooleanField(blank=False, null=False, default=True)
    peripheral_neuropathy_grade = models.IntegerField(blank=True, null=True)

    # Myeloma related
    cytogenic_markers = models.TextField(blank=True, null=True)  # csv
    molecular_markers = models.TextField(blank=True, null=True)  # csv
    stem_cell_transplant_history = models.JSONField(blank=True, null=True, default=list)
    plasma_cell_leukemia = models.BooleanField(blank=True, null=True, default=True)
    progression = models.TextField(blank=True, null=True)

    # Lymphoma related
    gelf_criteria_status = models.TextField(blank=True, null=True)  # csv
    flipi_score = models.IntegerField(blank=True, null=True)
    flipi_score_options = models.TextField(blank=True, null=True)  # csv
    tumor_grade = models.TextField(blank=True, null=True)  # csv

    # not in use
    heartrate = models.IntegerField(help_text="Patient's heart rate", blank=True, null=True)
    heartrate_variability = models.IntegerField(help_text="Patient's heart rate variability", blank=True, null=True)


    # ---------------
    # Treatment block
    # ---------------

    prior_therapy = models.TextField(blank=True, null=True)
    first_line_therapy = models.TextField(blank=True, null=True)
    first_line_date = models.DateField(blank=True, null=True)
    first_line_outcome = models.TextField(blank=True, null=True)  # enum
    second_line_therapy = models.TextField(blank=True, null=True)
    second_line_date = models.DateField(blank=True, null=True)
    second_line_outcome = models.TextField(blank=True, null=True)  # enum
    later_therapy = models.TextField(blank=True, null=True)
    later_date = models.DateField(blank=True, null=True)
    later_outcome = models.TextField(blank=True, null=True)  # enum
    relapse_count = models.IntegerField(blank=True, null=True)
    treatment_refractory_status = models.CharField(max_length=255, blank=True, null=True)

    # deprecated
    therapy_lines_count = models.IntegerField(blank=True, null=True)
    line_of_therapy = models.TextField(blank=True, null=True)


    # -----------
    # Blood block
    # -----------

    absolute_neutrophile_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    absolute_neutrophile_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/UL',
        help_text="Units for the patient's absolute neutrophile count"
    )
    platelet_count = models.IntegerField(blank=True, null=True)
    platelet_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/UL',
        help_text="Units for the patient's platelet count"
    )
    white_blood_cell_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    white_blood_cell_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/L',
        help_text="Units for the patient's white blood cell count"
    )
    red_blood_cell_count = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    red_blood_cell_count_units = models.CharField(
        max_length=10,
        choices=PlateletCountUnits.choices,
        blank=True,
        null=True,
        default='CELLS/L',
        help_text="Units for the patient's red blood cell count"
    )
    serum_calcium_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_calcium_level_units = models.CharField(
        max_length=15,
        choices=SerumCalciumUnits.choices,
        blank=True,
        null=True,
        default='MG/DL',
        help_text="Units for the patient's serum calcium level"
    )
    creatinine_clearance_rate = models.IntegerField(blank=True, null=True)
    serum_creatinine_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    serum_creatinine_level_units = models.CharField(
        max_length=15,
        choices=SerumCreatinineUnits.choices,
        blank=True,
        null=True,
        default='MG/DL',
        help_text="Units for the patient's serum creatinine level"
    )
    hemoglobin_level = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    hemoglobin_level_units = models.CharField(
        max_length=5,
        choices=HemoglobinUnits.choices,
        blank=True,
        null=True,
        default='G/DL',
        help_text="Units for the patient's hemoglobin level"
    )
    bone_lesions = models.TextField(blank=True, null=True)
    meets_crab = models.BooleanField(blank=True, null=True)

    estimated_glomerular_filtration_rate = models.IntegerField(blank=True, null=True)
    liver_enzyme_levels_ast = models.IntegerField(blank=True, null=True)
    liver_enzyme_levels_alt = models.IntegerField(blank=True, null=True)
    serum_bilirubin_level_total = models.IntegerField(blank=True, null=True)
    serum_bilirubin_level_total_units = models.CharField(
        max_length=15,
        choices=SerumBilirubinUnits.choices,
        blank=True,
        null=True,
        default='MG/DL',
        help_text="Units for the patient's total serum bilirubin level"
    )
    serum_bilirubin_level_direct = models.IntegerField(blank=True, null=True)
    serum_bilirubin_level_direct_units = models.CharField(
        max_length=15,
        choices=SerumBilirubinUnits.choices,
        blank=True,
        null=True,
        default='MG/DL',
        help_text="Units for the patient's direct serum bilirubin level"
    )
    clonal_bone_marrow_plasma_cells_percentage = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    kappa_flc = models.IntegerField(blank=True, null=True)
    lambda_flc = models.IntegerField(blank=True, null=True)
    meets_slim = models.BooleanField(blank=True, null=True)


    # ----------
    # Labs block
    # ----------

    monoclonal_protein_serum = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    monoclonal_protein_urine = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    lactate_dehydrogenase_level = models.IntegerField(blank=True, null=True)
    pulmonary_function_test_result = models.BooleanField(blank=False, null=False, default=False)
    bone_imaging_result = models.BooleanField(blank=False, null=False, default=False)
    clonal_plasma_cells = models.IntegerField(blank=True, null=True)
    ejection_fraction = models.IntegerField(blank=True, null=True)


    # --------------
    # Behavior block
    # --------------

    consent_capability = models.BooleanField(help_text="Does the patient have cognitive ability to consent?", blank=False, null=False, default=True)
    caregiver_availability_status = models.BooleanField(help_text="Is there an available caregiver for the patient?", blank=False, null=False, default=False)
    contraceptive_use = models.BooleanField(help_text="Does the patient use contraceptives?", blank=False, null=False, default=False)
    no_pregnancy_or_lactation_status = models.BooleanField(help_text="Does the patient self assess as not pregnant or lactating?", blank=False, null=False, default=True)
    pregnancy_test_result = models.BooleanField(help_text="Does the female patient of childbearing age have a negative test result for pregnancy?", blank=False, null=False, default=False)
    no_mental_health_disorder_status = models.BooleanField(help_text="Does the patient have a mental health disorder?", blank=False, null=False, default=True)
    no_concomitant_medication_status = models.BooleanField(help_text="Does the patient have concomitant medication?", blank=False, null=False, default=True)
    no_tobacco_use_status = models.BooleanField(help_text="Does the patient use tobacco?", blank=False, null=False, default=True)
    no_substance_use_status = models.BooleanField(help_text="Does the patient use substances?", blank=False, null=False, default=True)
    no_geographic_exposure_risk = models.BooleanField(help_text="Has the patient had geographic exposure to risk?", blank=False, null=False, default=True)

    no_hiv_status = models.BooleanField(help_text="Does the patient has had HIV?", blank=False, null=False, default=True)
    no_hepatitis_b_status = models.BooleanField(help_text="Does the patient has had Hepatitis B (HBV)?", blank=False, null=False, default=True)
    no_hepatitis_c_status = models.BooleanField(help_text="Does the patient has had Hepatitis C (HCV)?", blank=False, null=False, default=True)

    # ----------------------------
    # other / unknown / deprecated
    # ----------------------------

    remission_duration_min = models.TextField(blank=True, null=True)  # str for now
    washout_period_duration = models.TextField(blank=True, null=True)  # str for now

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
