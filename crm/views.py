from django.shortcuts import render, redirect, get_object_or_404
from portal.models import Application, School, Department, Student, Year, Semester, Headline, Notification, Course, Grade
from django.contrib.auth.decorators import user_passes_test,login_required
from .forms import ApplicationForm, StudentForm, CrmLoginForm, HeadlineForm, NotificationForm, SchoolForm, DepartmentForm, CourseForm, GradeForm
from django.db.models import Count
from django.db.models.expressions import RawSQL
from datetime import datetime
from django.contrib import messages
from django.db.models.functions import ExtractMonth
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse
from collections import defaultdict

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
def crm_dashboard(request):
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
        application_number=application.application_number,
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
        year = application.year,
        semester = application.semester,
    
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



def move_to_new_semester(request):
    students = Student.objects.all()

    for student in students:
        current_year = student.year
        current_semester = student.semester

        # Get First and Second semester for this year
        first_semester = Semester.objects.filter(name="First", year=current_year).first()
        second_semester = Semester.objects.filter(name="Second", year=current_year).first()

        if not first_semester or not second_semester:
            messages.error(request, f"Error: Year {current_year.number} does not have both semesters!")
            return redirect("crm_dashboard")

        # Move to next semester or next year
        if current_semester == first_semester:
            student.semester = second_semester
        else:
            next_year = Year.objects.filter(number=current_year.number + 1).first()
            if next_year:
                student.year = next_year
                student.semester = Semester.objects.filter(name="First", year=next_year).first()
            else:
                student.status = "Graduated"  # Final year students graduate

        student.save()

    messages.success(request, "All students moved to the new semester successfully!")
    return redirect("semester_success")


def move_semester_confirmationPage(request):
    """Renders the confirmation page before processing the semester update."""
    if request.method == "POST":
        return redirect("move_semester")  # Redirect to the actual move function

    return render(request, "crm/crm_move_confirmation_page.html")


def semester_success(request):
    return render(request, "crm/crm_move_semester_success_page.html")


def move_to_previous_semester(request):
    students = Student.objects.all()

    for student in students:
        current_year = student.year
        current_semester = student.semester

        # Get First and Second semester for this year
        first_semester = Semester.objects.filter(name="First", year=current_year).first()
        second_semester = Semester.objects.filter(name="Second", year=current_year).first()

        if not first_semester or not second_semester:
            messages.error(request, f"Error: Year {current_year.number} does not have both semesters!")
            return redirect("crm_dashboard")

        # Move back to the previous semester or year
        if current_semester == second_semester:
            student.semester = first_semester  # Move back to First Semester
        else:
            prev_year = Year.objects.filter(number=current_year.number - 1).first()
            if prev_year:
                student.year = prev_year
                student.semester = Semester.objects.filter(name="Second", year=prev_year).first()
            else:
                messages.warning(request, f"Student {student} is already in the first semester of the first year and cannot go back further.")

        student.save()

    messages.success(request, "All students moved to the previous semester successfully!")
    return redirect("reverse_semester_success")


def reverse_semester_confirmationPage(request):
    """Renders the confirmation page before processing the semester update."""
    if request.method == "POST":
        return redirect("reverse_semester")  # Redirect to the actual move function

    return render(request, "crm/crm_reverse_comfirmation_page.html")


def semester_reverse_success(request):
    return render(request, "crm/crm_reverse_semester_success.html")



def Notify_student(request):
    if request.method == "POST":
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification Sent successfully!")
            return redirect("Notify_student")
        
    else:
        form = NotificationForm()

    notifications = paginate_notifications(request)

    return render(request, "crm/crm_post_notification.html", {"form":form, "notifications":notifications})    

def paginate_notifications(request):
    """ Helper function to paginate headlines """
    notification_list = Notification.objects.all()
    paginator = Paginator(notification_list, 3)  # 3 headlines per page
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)



def Post_headline(request):
    if request.method == "POST":
        form = HeadlineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Headline posted successfully!")
            return redirect("Post_headline")
    else:
        form = HeadlineForm()

    # Paginate headlines
    headlines = paginate_headlines(request)

    return render(request, "crm/crm_post_headline.html", {"form": form, "headlines": headlines})


def paginate_headlines(request):
    """ Helper function to paginate headlines """
    headlines_list = Headline.objects.all().order_by('-created_at')
    paginator = Paginator(headlines_list, 3)  # 3 headlines per page
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def Edit_headline(request, headline_id):
    headline = get_object_or_404(Headline, id=headline_id)

    if request.method == "POST":
        form = HeadlineForm(request.POST, request.FILES, instance=headline)
        if form.is_valid():
            form.save()
            messages.success(request, "Headline updated successfully!")
            return redirect("Post_headline")  # Ensure this is correct
    else:
        form = HeadlineForm(instance=headline)


    return render(request, "crm/crm_edit_post.html", {"form": form, "headline": headline})





def delete_headline(request, headline_id):
    headline = get_object_or_404(Headline, id=headline_id)
    
    if request.user.is_superuser:  # Ensure only superusers can delete
        headline.delete()
        messages.success(request, "Headline deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete this headline.")
    
    return redirect("Post_headline")  # Redirect to the headline list page

def school_view(request):
    schools = School.objects.all()

    return render(request, 'crm/crm_school_list.html', {'schools':schools})

def add_School(request):
    if request.method == "POST":
        form = SchoolForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "School created successfully!")
            return redirect("add_school")
    else:
        form = SchoolForm()

    # Paginate headlines
    schools = paginate_schools(request)

    return render(request, "crm/crm_add_school.html", {"form": form, "schools": schools})


def paginate_schools(request):
    """ Helper function to paginate headlines """
    schools_list = School.objects.all()
    paginator = Paginator(schools_list, 3)  # 3 headlines per page
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def department_view(request):
    departments = Department.objects.all()

    return render(request, 'crm/crm_department_list.html', {'departments':departments})

def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully!")
            return redirect("add_department")
    else:
        form = DepartmentForm()

    # Paginate headlines
    departments = paginate_departments(request)

    return render(request, "crm/crm_add_department.html", {"form": form, "departments": departments})

def paginate_departments(request):
    """ Helper function to paginate headlines """
    departments_list = Department.objects.all()
    paginator = Paginator(departments_list, 3)  # 3 headlines per page
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)




def course_view(request):
    courses = Course.objects.all()

    return render(request, 'crm/crm_course_list.html', {'courses':courses})

def add_course(request):
    schools = School.objects.all()
    departments = Department.objects.all()
    semesters = Semester.objects.all().order_by('-year', 'name')
    
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course {course.code} - {course.title} created successfully!")
            return redirect('add_course')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CourseForm()

    # Get all courses ordered by year and semester
    all_courses = Course.objects.all().order_by('semester__year', 'semester__name', 'code')
    
    # Group courses by year and semester for the dropdown
    courses_by_year_semester = {}
    for course in all_courses:
        year = course.semester.year if course.semester else "Unknown"
        semester_name = course.semester.name if course.semester else "Unknown"
        
        if year not in courses_by_year_semester:
            courses_by_year_semester[year] = {}
        
        if semester_name not in courses_by_year_semester[year]:
            courses_by_year_semester[year][semester_name] = []
        
        courses_by_year_semester[year][semester_name].append(course)
    
    # Paginate the flat course list
    paginator = Paginator(all_courses, 10)
    page_number = request.GET.get('page')
    courses = paginator.get_page(page_number)

    context = {
        "form": form,
        "courses": courses,
        "schools": schools,
        "departments": departments,
        "semesters": semesters,
        "courses_by_year_semester": courses_by_year_semester,
    }
    return render(request, "crm/crm_add_course.html", context)


def load_departments(request):
    school_id = request.GET.get('school_id')
    departments = Department.objects.filter(school_id=school_id).order_by('name')
    return JsonResponse(list(departments.values('id', 'name')), safe=False)



def add_grade(request):
    # Get all records
    schools = School.objects.all()
    departments = Department.objects.all()
    semesters = Semester.objects.all().order_by('-year', 'name')
    courses = Course.objects.all()
    students = Student.objects.all()

    if request.method == "POST":
        form = GradeForm(request.POST, request.FILES)
        if form.is_valid():
            grade = form.save()
            messages.success(request, f"Grade for {grade.student} in {grade.course} was successfully recorded!")
            return redirect('add_grade')  # Always redirect after successful POST
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GradeForm()

    context = {
        "form": form,
        "schools": schools,
        "departments": departments,
        "semesters": semesters,
        "courses": courses,
        "students": students
    }
    return render(request, "crm/crm_add_grade.html", context)


def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)

    if request.method == "POST":
        form = GradeForm(request.POST, request.FILES, instance=grade)
        if form.is_valid():
            updated_grade = form.save()
            messages.success(request, f"{updated_grade.course.title} grade updated successfully!")
            return redirect("grade_list")
    else:
        form = GradeForm(instance=grade)

    return render(request, "crm/edit_grade.html", {"form": form, "grade": grade})


def grade_list(request):
    grades = Grade.objects.select_related('student', 'course', 'semester').order_by('student__surname')
    return render(request, 'crm/grade_list.html', {'grades': grades})



def load_courses(request):
    semester_id = request.GET.get('semester_id')
    courses = Course.objects.filter(semester_id=semester_id).order_by('title')
    return JsonResponse(list(courses.values('id', 'title', 'code')), safe=False)


def load_departments(request):
    school_id = request.GET.get('school_id')
    departments = Department.objects.filter(school_id=school_id).order_by('name')
    return JsonResponse(list(departments.values('id', 'name')), safe=False)