from django.db import models
import uuid

# -------------------
# User Roles
# -------------------
ROLE_CHOICES = [
    ('doctor', 'Doctor'),
    ('nurse', 'Nurse'),
    ('admin', 'Admin'),
]

class AppUser(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=100)
    usermail = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------
# Patient Model
# -------------------
class Patient(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Follow-up', 'Follow-up'),
        ('Chronic', 'Chronic'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=10, unique=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and last_patient.patient_id:
                last_id = int(last_patient.patient_id.replace('PO', ''))
            else:
                last_id = 0
            new_id = last_id + 1
            self.patient_id = f'PO{new_id:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

from django.db import models
import uuid

# -------------------
# User Roles
# -------------------
ROLE_CHOICES = [
    ('doctor', 'Doctor'),
    ('nurse', 'Nurse'),
    ('admin', 'Admin'),
]

class AppUser(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=100)
    usermail = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------
# Patient Model
# -------------------
class Patient(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Follow-up', 'Follow-up'),
        ('Chronic', 'Chronic'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    patient_id = models.CharField(max_length=10, unique=True, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient and last_patient.patient_id:
                last_id = int(last_patient.patient_id.replace('PO', ''))
            else:
                last_id = 0
            new_id = last_id + 1
            self.patient_id = f'PO{new_id:05d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -------------------
# Visit Model (New Visit Feature)
# -------------------
class Visit(models.Model):
    CHECKUP_TYPE_CHOICES = [
        ('Follow-up', 'Follow-up'),
        ('Regular', 'Regular'),
        ('New', 'New'),
    ]

    HEALTHCARE_SERVICE_CHOICES = [
        ('OPD', 'OPD'),
        ('IPD', 'IPD'),
        ('Emergency', 'Emergency'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    doctor_name = models.CharField(max_length=100)
    date = models.DateField()
    checkup_type = models.CharField(max_length=50, choices=CHECKUP_TYPE_CHOICES)
    healthcare_service = models.CharField(max_length=50, choices=HEALTHCARE_SERVICE_CHOICES)
    bp = models.CharField(max_length=15)  # Example: 120/80 mmHg
    oxygen_level = models.CharField(max_length=10)  # Example: 98%
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # Example: 72.50
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Visit - {self.patient.name} on {self.date}"


# -------------------
# DischargeSummary (New Visit Feature)
# -------------------

from django.db import models
from .models import Patient  # assuming Patient already exists

class DischargeSummary(models.Model):
    DISCHARGE_TYPE_CHOICES = [
        ('Planned', 'Planned'),
        ('DAMA', 'Discharged Against Medical Advice'),
        ('DOR', 'Discharged on Request'),
        ('LAMA', 'Left Against Medical Advice'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='discharges')
    uhid = models.CharField(max_length=50)
    ip_id = models.CharField(max_length=50, blank=True, null=True)
    ward = models.CharField(max_length=100, blank=True, null=True)
    bed_no = models.CharField(max_length=20, blank=True, null=True)
    consultant_name = models.CharField(max_length=100)
    admission_date = models.DateField()
    discharge_date = models.DateField()

    final_diagnosis = models.TextField()
    procedures_done = models.TextField(blank=True, null=True)
    clinical_examination = models.TextField(blank=True, null=True)
    consultations = models.TextField(blank=True, null=True)

    discharge_type = models.CharField(max_length=20, choices=DISCHARGE_TYPE_CHOICES, default='Planned')
    chief_complaints = models.TextField(blank=True, null=True)
    past_history = models.TextField(blank=True, null=True)
    hospital_course = models.TextField(blank=True, null=True)
    condition_on_discharge = models.TextField(blank=True, null=True)

    discharge_advice = models.TextField(blank=True, null=True)
    diet_advice = models.TextField(blank=True, null=True)
    follow_up = models.TextField(blank=True, null=True)
    emergency_instructions = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discharge Summary - {self.patient.name} ({self.discharge_date})"
