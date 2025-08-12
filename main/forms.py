from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['patient_id']


# forms.py
from django import forms
from .models import DischargeSummary

class DischargeSummaryForm(forms.ModelForm):
    class Meta:
        model = DischargeSummary
        fields = [
            'patient', 'uhid', 'ip_id', 'ward', 'bed_no', 'consultant_name',
            'admission_date', 'discharge_date', 'final_diagnosis', 'procedures_done',
            'clinical_examination', 'consultations', 'discharge_type', 'chief_complaints',
            'past_history', 'hospital_course', 'condition_on_discharge',
            'discharge_advice', 'diet_advice', 'follow_up', 'emergency_instructions'
        ]
        widgets = {
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'discharge_date': forms.DateInput(attrs={'type': 'date'}),
            'final_diagnosis': forms.Textarea(attrs={'rows': 2}),
            'procedures_done': forms.Textarea(attrs={'rows': 2}),
            'hospital_course': forms.Textarea(attrs={'rows': 3}),
            'discharge_advice': forms.Textarea(attrs={'rows': 2}),
        }
