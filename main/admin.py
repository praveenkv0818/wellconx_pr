from django.contrib import admin
from .models import AppUser, Patient,Visit,DischargeSummary


# Register your models here.
admin.site.register(AppUser)
admin.site.register(Patient)
admin.site.register(Visit)
admin.site.register(DischargeSummary)