from django.urls import path
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # Patient Management
    path('ehr_home/', views.ehr_home, name='ehr_home'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('api/patient/<str:patient_id>/', views.patient_api, name='patient_api'),
    path('patient/<str:patient_id>/edit/', views.edit_patient, name='edit_patient'),

    # Other Views
    path('access-control/', views.access_control_view, name='access_control'),
    path('clinical_docs/', views.clinical_docs_view, name='clinical_docs'),
    path('investigations/', views.investigations_view, name='investigations'),
    path('prescriptions/', views.prescriptions_view, name='prescriptions'),

    # Visits
    path('visit_history/', views.visit_history_view, name='visit_history'),
    path('new_visit/', views.new_visit, name='new_visit'),
    path('patients/search/', views.patient_search, name='patient_search'),
    #discharge
    path('discharge/add/', views.add_discharge_summary, name='add_discharge_summary'),
    path('discharge/add/<str:patient_id>/', views.add_discharge_summary, name='add_discharge_summary_for_patient'),
    path('discharge/list/', views.discharge_summary_list, name='discharge_summary_list'),
    path('discharge/<int:pk>/', views.discharge_summary_detail, name='discharge_summary_detail'),
   path('discharge/<int:pk>/pdf/', views.discharge_summary_pdf, name='discharge_summary_pdf'),

    # API for patient details (for auto-fill)
    path('api/patient-details/<str:patient_id>/', views.get_patient_details, name='get_patient_details'),
]
