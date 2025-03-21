from django.shortcuts import render, redirect, get_object_or_404
from portal.models import Application, School, Department, Student
from django.contrib.auth.decorators import user_passes_test,login_required
from .forms import ApplicationForm, StudentForm, CrmLoginForm
from django.db.models import Count
from django.db.models.expressions import RawSQL
from datetime import datetime
from django.contrib import messages
from django.db.models.functions import ExtractMonth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

# Create your views here.



def Crmlogin(request):
    if request.method == "POST":
        form = CrmLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            # Check if a user exists with this email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "User with this email does not exist.")
                return render(request, "crm/crm_login.html", {"form": form})

            # Authenticate user
            user = authenticate(request, username=user.username, password=password)

            if user is not None and user.is_superuser:  # Ensure only superusers can log in
                login(request, user)
                return redirect("crm_dashboard")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = CrmLoginForm()

    return render(request, "crm/crm_login.html", {"form": form})

def is_superuser(user):
    """Check if the user is a superuser."""
    return user.is_superuser


@user_passes_test(is_superuser)
@login_required(login_url="crm_login")
def dashboard(request):
    # Fetch counts for dashboard metrics
    total_applications = Application.objects.count()
    total_schools = School.objects.count()
    total_departments = Department.objects.count()
    pending_applications = Application.objects.filter(is_approved=False).count()
    admitted_students = Student.objects.count()

    # Applications by Month (Compatible with SQLite & PostgreSQL)
    applications_by_month = (
        Application.objects.annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    # Format months and counts for the chart
    months = [datetime.strptime(str(item["month"]), "%m").strftime("%b") for item in applications_by_month if item["month"]]
    application_counts = [item["count"] for item in applications_by_month]

    # Fetch recent applications
    recent_applications = Application.objects.order_by("-id")[:5]

    context = {
        "total_applications": total_applications,
        "total_schools": total_schools,
        "total_departments": total_departments,
        "pending_applications": pending_applications,
        "admitted_students": admitted_students,
        "recent_applications": recent_applications,
        "months": months,
        "application_counts": application_counts,
    }

    return render(request, "crm/crm_dashboard.html", context)


def applicant_list(request):
    applications = Application.objects.all()

    # Group applications by school and department
    grouped_applications = {}
    for app in applications:
        school = app.school.name
        department = app.department.name

        if school not in grouped_applications:
            grouped_applications[school] = {}
        if department not in grouped_applications[school]:  # Fixed variable case
            grouped_applications[school][department] = []

        grouped_applications[school][department].append(app)

    return render(request, "crm/applicant_list.html", {"grouped_applications": grouped_applications})


def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            return redirect("view_applicant", application_id=application.id)  # Redirect to the CRM dashboard or list page
    else:
        form = ApplicationForm(instance=application)
    
    return render(request, "crm/edit_application.html", {"form": form, "application": application})





def student_list(request):
    students = Student.objects.all()

    # Group students by school and department
    grouped_students = {}
    for student in students:
        school = student.school.name
        department = student.department.name

        if school not in grouped_students:
            grouped_students[school] = {}
        if department not in grouped_students[school]:  # Fixed variable case
            grouped_students[school][department] = []

        grouped_students[school][department].append(student)

    return render(request, "crm/student_list.html", {"grouped_students": grouped_students})



def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("student_list")  # Redirect to the CRM dashboard or list page
    else:
        form = StudentForm(instance=student)
    
    return render(request, "crm/edit_student.html", {"form": form, "student": student})



def view_applicant(request, application_id):
    applicant = get_object_or_404(Application, id=application_id)
    return render(request, "crm/applicant_profile.html", {"applicant": applicant})


def view_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, "crm/student_profile.html", {"student": student})



def approve_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    # Check if a student with the same application number already exists
    if Student.objects.filter(application_number=application.application_number).exists():
        messages.warning(request, f"Student with application number {application.application_number} already exists!")
        return redirect("applicant_list")

    # Create Student record
    student = Student.objects.create(
        application_number=application.application_number,  # This was missing
        surname=application.surname,
        first_name=application.first_name,
        other_name=application.other_name,
        email=application.email,
        phone_number=application.phone_number,
        address=application.address,
        state_of_origin=application.state_of_origin,
        local_government=application.local_government,
        date_of_birth=application.date_of_birth,
        school=application.school,
        department=application.department,
        academic_session=application.academic_session,
        profile_picture=application.profile_picture,
    )

    # Mark application as approved
    application.is_approved = True
    application.save()

    messages.success(request, f"Application {application.application_number} has been approved and student created.")
    return redirect("applicant_list")


def revoke_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    # Check if a student exists with this application number and delete it
    student = Student.objects.filter(application_number=application.application_number).first()
    if student:
        student.delete()
        print(f"🚨 Student {application.application_number} record deleted.")

    # Mark application as not approved
    application.is_approved = False
    application.save()

    print(f"🚫 Application {application.application_number} has been revoked.")
    return redirect("applicant_list")