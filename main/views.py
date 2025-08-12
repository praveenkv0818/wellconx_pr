from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse, Http404, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from .models import AppUser, Patient, Visit, DischargeSummary
from .forms import PatientForm
from django.template.loader import render_to_string
import pdfkit


# -------------------- Authentication --------------------
def custom_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = AppUser.objects.get(usermail=email)
            if check_password(password, user.password):
                request.session['user_id'] = str(user.unique_id)
                request.session['username'] = user.username
                request.session['role'] = user.role
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except AppUser.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        usermail = request.POST['usermail']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST['role']

        if password1 != password2:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        if AppUser.objects.filter(usermail=usermail).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        AppUser.objects.create(
            username=username,
            usermail=usermail,
            password=make_password(password1),
            role=role
        )
        messages.success(request, "User registered successfully.")
        return redirect('login')

    return render(request, 'register.html')


def dashboard(request):
    if not request.session.get('user_id'):
        return redirect('login')
    return render(request, 'dashboard.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# -------------------- Patient Management --------------------
def ehr_home(request):
    patients = Patient.objects.all()
    role = request.session.get('role')
    return render(request, 'ehr_home.html', {'patients': patients, 'role': role})


def add_patient(request):
    if request.session.get('role') != "admin":
        return HttpResponseForbidden("You are not authorized to access this page.")

    last_patient = Patient.objects.order_by('-id').first()
    if last_patient and last_patient.patient_id:
        last_id = int(last_patient.patient_id.replace('PO', ''))
    else:
        last_id = 0
    next_patient_id = f'PO{last_id + 1:05d}'

    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.patient_id = next_patient_id
            patient.save()
            return redirect('ehr_home')
    else:
        form = PatientForm()

    return render(request, 'add_patient.html', {'form': form, 'next_patient_id': next_patient_id})


def patient_api(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        raise Http404("Patient not found")

    data = {
        'name': patient.name,
        'patient_id': patient.patient_id,
        'age': patient.age,
        'status': patient.status,
        'last_visit': None,
        'primary_condition': None,
    }
    return JsonResponse(data)


def edit_patient(request, patient_id):
    if request.session.get('role') != "admin":
        return HttpResponseForbidden("You are not authorized to access this page.")

    patient = get_object_or_404(Patient, patient_id=patient_id)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('ehr_home')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'edit_patient.html', {'form': form, 'patient': patient})


# -------------------- Other Views --------------------
def access_control_view(request):
    doctor_count = AppUser.objects.filter(role='doctor').count()
    nurse_count = AppUser.objects.filter(role='nurse').count()
    admin_count = AppUser.objects.filter(role='admin').count()

    return render(request, 'access_control.html', {
        'doctor_count': doctor_count,
        'nurse_count': nurse_count,
        'admin_count': admin_count,
    })


def clinical_docs_view(request):
    return render(request, 'clinical_docs.html')


def discharge_view(request):
    return render(request, 'discharge.html')


def investigations_view(request):
    return render(request, 'investigations.html')


def prescriptions_view(request):
    return render(request, 'prescriptions.html')


def visit_history_view(request):
    recent_patients = Patient.objects.order_by('-id')[:2]
    if not recent_patients:
        visits = Visit.objects.none()
    else:
        visits = Visit.objects.select_related('patient').filter(
            patient__in=recent_patients
        ).order_by('-date')
    return render(request, 'visit_history.html', {'visits': visits})


# -------------------- New Visit --------------------
def new_visit(request):
    patients = Patient.objects.order_by('-id')[:2]

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        if patient_id:
            patient = get_object_or_404(Patient, id=patient_id)
            Visit.objects.create(
                patient=patient,
                date=request.POST.get('date'),
                doctor_name=request.POST.get('doctor_name'),
                checkup_type=request.POST.get('checkup_type'),
                healthcare_service=request.POST.get('healthcare_service'),
                bp=request.POST.get('bp'),
                oxygen_level=request.POST.get('oxygen_level'),
                weight=request.POST.get('weight'),
                notes=request.POST.get('notes'),
            )
        return redirect('visit_history')

    return render(request, 'new_visit.html', {'patients': patients})

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import pdfkit

from .models import Patient, DischargeSummary 

# patient search enable ------------
from django.http import JsonResponse
from .models import Patient

def patient_search(request):
    term = request.GET.get('term', '')  # Select2 sends `term`
    # simple case-insensitive name search; limit to 20 results
    patients = Patient.objects.filter(name__icontains=term).order_by('name')[:20]

    results = [
        {"id": p.id, "text": f"{p.name} ({p.age} yrs, {p.gender})"}
        for p in patients
    ]
    return JsonResponse({"results": results})

# -------------------- Add Discharge Summary --------------------
def add_discharge_summary(request, patient_id=None):
    patients = Patient.objects.all()
    selected_patient = None

    if patient_id:
        selected_patient = get_object_or_404(Patient, patient_id=patient_id)

    # List of textarea fields with labels, in order you want to display
    text_fields = [
        ('final_diagnosis', 'Final Diagnosis'),
        ('procedures_done', 'Procedures Done'),
        ('clinical_examination', 'Clinical Examination'),
        ('consultations', 'Consultations'),
        ('chief_complaints', 'Chief Complaints'),
        ('past_history', 'Past History'),
        ('hospital_course', 'Hospital Course'),
        ('condition_on_discharge', 'Condition on Discharge'),
        ('discharge_advice', 'Discharge Advice'),
        ('diet_advice', 'Diet Advice'),
        ('follow_up', 'Follow Up'),
        ('emergency_instructions', 'Emergency Instructions'),
    ]

    if request.method == 'POST':
        patient_pk = request.POST.get('patient')
        patient_obj = None
        if patient_pk:
            patient_obj = Patient.objects.filter(patient_id=patient_pk).first()

        DischargeSummary.objects.create(
            patient=patient_obj,
            uhid=request.POST.get('uhid', ''),
            ip_id=request.POST.get('ip_id', ''),
            ward=request.POST.get('ward', ''),
            bed_no=request.POST.get('bed_no', ''),
            consultant_name=request.POST.get('consultant_name', ''),
            admission_date=request.POST.get('admission_date') or None,
            discharge_date=request.POST.get('discharge_date') or None,
            discharge_type=request.POST.get('discharge_type', ''),
            final_diagnosis=request.POST.get('final_diagnosis', ''),
            procedures_done=request.POST.get('procedures_done', ''),
            clinical_examination=request.POST.get('clinical_examination', ''),
            consultations=request.POST.get('consultations', ''),
            chief_complaints=request.POST.get('chief_complaints', ''),
            past_history=request.POST.get('past_history', ''),
            hospital_course=request.POST.get('hospital_course', ''),
            condition_on_discharge=request.POST.get('condition_on_discharge', ''),
            discharge_advice=request.POST.get('discharge_advice', ''),
            diet_advice=request.POST.get('diet_advice', ''),
            follow_up=request.POST.get('follow_up', ''),
            emergency_instructions=request.POST.get('emergency_instructions', ''),
        )
        return redirect('discharge_summary_list')

    return render(request, 'add_discharge_summary.html', {
        'patients': patients,
        'selected_patient': selected_patient,
        'text_fields': text_fields,   # <-- Pass this to template!
    })



# -------------------- Patient Details API --------------------
def get_patient_details(request, patient_id):
    try:
        patient = Patient.objects.get(patient_id=patient_id)
        data = {
            'name': patient.name,
            'age': patient.age,
            'gender': patient.gender,
            'contact_number': patient.contact_number,
        }
    except Patient.DoesNotExist:
        data = {'error': 'Patient not found'}
    return JsonResponse(data)


# -------------------- Discharge Summary List & Detail --------------------
def discharge_summary_list(request):
    summaries = DischargeSummary.objects.select_related('patient').all().order_by('-discharge_date')
    return render(request, 'discharge_summary_list.html', {'summaries': summaries})



def discharge_summary_detail(request, pk):
    summary = get_object_or_404(DischargeSummary, pk=pk)
    return render(request, 'discharge_summary_detail.html', {'summary': summary})



# -------------------- PDF Export --------------------
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from .models import DischargeSummary

def discharge_summary_pdf(request, pk):
    # Get the object
    summary = get_object_or_404(DischargeSummary, pk=pk)

    # Render the HTML template to a string
    html_string = render_to_string('discharge_summary_pdf.html', {'summary': summary, 'request': request})

    # Create a bytes buffer for the PDF
    result = BytesIO()

    # Note: base_url helps xhtml2pdf resolve static files if you use absolute URLs
    # We'll use the site's absolute root (works for absolute URL static paths)
    base_url = request.build_absolute_uri('/')  # e.g. http://127.0.0.1:8000/

    # Create PDF
    pisa_status = pisa.CreatePDF(src=html_string, dest=result, link_callback=lambda uri, rel: _link_callback(uri, rel, base_url))

    if pisa_status.err:
        # Return an error response with the HTML for debugging (or log it)
        return HttpResponse('We had some errors generating PDF:<br/>' + str(pisa_status.err), status=500)

    # Return PDF response
    result.seek(0)
    response = HttpResponse(result.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=discharge_summary_{pk}.pdf'
    return response


# helper function to map URIs used in templates to absolute filesystem or URL paths
import os
from django.conf import settings
from urllib.parse import urljoin, urlparse
def _link_callback(uri, rel, base_url):
    """
    Convert HTML URIs (static/media) to absolute paths for xhtml2pdf.
    - uri: URI from the HTML (like /static/css/style.css or /media/image.png or http://...)
    - rel: relative path (unused)
    - base_url: request.build_absolute_uri('/') => 'http://127.0.0.1:8000/'

    Returns an absolute URL or absolute filesystem path xhtml2pdf can read.
    """
    parsed = urlparse(uri)
    # If URI is already absolute (http/https), return as-is
    if parsed.scheme in ('http', 'https'):
        return uri

    # If it starts with STATIC_URL or MEDIA_URL, build absolute filesystem path
    # Adjust depending on your STATIC settings
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, uri.lstrip('/'))
        if os.path.exists(path):
            return path
        # fallback to absolute URL
        return urljoin(base_url, uri.lstrip('/'))
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, '').lstrip('/'))
        if os.path.exists(path):
            return path
        return urljoin(base_url, uri.lstrip('/'))

    # Default: try filesystem relative to BASE_DIR
    path = os.path.join(settings.BASE_DIR, uri.lstrip('/'))
    if os.path.exists(path):
        return path

    # Otherwise return absolute URL
    return urljoin(base_url, uri.lstrip('/'))
