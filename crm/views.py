from django.shortcuts import render, redirect, get_object_or_404
from portal.models import Application, School, Course, Student
from django.contrib.auth.decorators import user_passes_test
from .forms import ApplicationForm, StudentForm
from django.db.models import Count
from django.db.models.expressions import RawSQL
from datetime import datetime
from django.contrib import messages

# Create your views here.


def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def dashboard(request):
    total_applications = Application.objects.count()
    total_schools = School.objects.count()
    total_courses = Course.objects.count()
    pending_applications = Application.objects.filter(is_approved=False).count()  # Adjust filter to show pending applications
    admitted_students = Student.objects.count()

    # Applications by Month using SQLite-compatible function
    applications_by_month = (
        Application.objects.annotate(
            month=RawSQL("strftime('%m', date_of_birth)", ())
        )
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Convert month numbers to month names (e.g., 01 → Jan)
    months = [datetime.strptime(item['month'], "%m").strftime("%b") for item in applications_by_month]
    application_counts = [item['count'] for item in applications_by_month]

    # Fetch the 5 most recent applications
    recent_applications = Application.objects.order_by('-id')[:5]

    context = {
        'total_applications': total_applications,
        'total_schools': total_schools,
        'total_courses': total_courses,
        'pending_applications': pending_applications,
        'admitted_students' : admitted_students,
        'recent_applications': recent_applications,
        'months': months,
        'application_counts': application_counts,
    }

    return render(request, 'dashboard.html', context)


def applicant_list(request):
    applications = Application.objects.all()  # Fetch all applications

    # Group applications by school and course
    grouped_applications = {}
    for app in applications:
        school = app.school.name  # Assuming `school` is a ForeignKey in Application model
        course = app.course.name  # Assuming `course` is a ForeignKey in Application model

        if school not in grouped_applications:
            grouped_applications[school] = {}
        if course not in grouped_applications[school]:
            grouped_applications[school][course] = []
        
        grouped_applications[school][course].append(app)

    return render(request, "applicant_list.html", {"grouped_applications": grouped_applications})


def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            return redirect("view_applicant", application_id=application.id)  # Redirect to the CRM dashboard or list page
    else:
        form = ApplicationForm(instance=application)
    
    return render(request, "edit_application.html", {"form": form, "application": application})





def student_list(request):
    students = Student.objects.all()  # Fetch all applications

    # Group applications by school and course
    grouped_students = {}
    for student in students:
        school = student.school.name  # Assuming `school` is a ForeignKey in Application model
        course = student.course.name  # Assuming `course` is a ForeignKey in Application model

        if school not in grouped_students:
            grouped_students[school] = {}
        if course not in grouped_students[school]:
            grouped_students[school][course] = []
        
        grouped_students[school][course].append(student)

    return render(request, "student_list.html", {"grouped_students": grouped_students})


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("student_list")  # Redirect to the CRM dashboard or list page
    else:
        form = StudentForm(instance=student)
    
    return render(request, "edit_student.html", {"form": form, "student": student})



def view_applicant(request, application_id):
    applicant = get_object_or_404(Application, id=application_id)
    return render(request, "applicant_profile.html", {"applicant": applicant})



def approve_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    # Check if a student with the same application number already exists
    if Student.objects.filter(application_number=application.application_number).exists():
        print(f"⚠️ Student with application number {application.application_number} already exists!")
        return redirect("applicant_list")  # Redirect to an error page or handle it gracefully

    # Create Student record
    student = Student.objects.create(
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
        course=application.course,
        application_number=application.application_number,
        profile_picture=application.profile_picture
    )

    # ✅ Mark application as approved instead of deleting
    application.is_approved = True
    application.save()

    print(f"✅ Application {application.application_number} approved and student created.")
    return redirect("applicant_list")  # Redirect to the list of applicants



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