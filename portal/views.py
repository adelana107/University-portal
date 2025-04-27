from django.shortcuts import render, redirect, get_object_or_404
from .forms import ApplicationForm, StudentLoginForm
from .models import Application, Department, State, Lga, Student, Course, Year, RegisteredCourse, Headline, Category, Notification   # Ensure you import your model
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ApplicantLoginForm
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

# Create your views here.


@login_required
@require_POST
def clear_all_notifications(request):
    try:
        # Delete all notifications for the current user
        deleted_count = Notification.objects.filter(user=request.user).delete()[0]
        
        return JsonResponse({
            'success': True,
            'count': deleted_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)



@login_required
@require_POST
def mark_all_notifications_read(request):
    try:
        # Update all unread notifications for the current user
        updated = Notification.objects.filter(
            user=request.user,
            read=False
        ).update(
            read=True,
            read_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'count': updated
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)




@require_POST
@csrf_exempt  # Only use this if you're having CSRF issues - better to properly handle CSRF
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)

@login_required
@require_POST
def update_profile_picture(request):
    if 'profile_picture' in request.FILES:
        # Handle the file upload here
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


def applicant_login(request):
    if request.method == "POST":
        form = ApplicantLoginForm(request.POST)
        if form.is_valid():
            application_number = form.cleaned_data["application_number"]
            surname = form.cleaned_data["surname"]

            # Authenticate using the application number as username
            user = authenticate(request, username=application_number, password=surname)
            
            if user:
                login(request, user)
                return redirect("application_profile")  # Redirect to profile page
            else:
                return render(request, "applicant_portal_login.html", {"form": form, "error": "Invalid application number or surname."})
    else:
        form = ApplicantLoginForm()

    return render(request, "applicant_portal_login.html", {"form": form})


def student_login(request):
    if request.method == "POST":
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            application_number = form.cleaned_data["application_number"]
            surname = form.cleaned_data["surname"]

            # Authenticate using application number as username
            user = authenticate(request, username=application_number, password=surname)
            
            if user:
                login(request, user)
                return redirect("student_portal")  # Redirect to student profile
            else:
                return render(request, "student_portal_login.html", {
                    "form": form,
                    "error": "Invalid application number or surname."
                })
    else:
        form = StudentLoginForm()

    return render(request, "student_portal_login.html", {"form": form})




def home(request):
    return render(request, 'home.html')




@login_required
def applicant_profile(request):
    user = request.user  # Get the logged-in user
    applications = Application.objects.filter(application_number=user.username)  # Fetch their application
    students = Student.objects.filter(application_number=user.username).first()

    if students:
        
        return redirect("admission_success", students.application_number, students.surname )

    return render(request, "application_profile.html", {"applications": applications, "students": students})



@login_required
def student_portal(request):
    user = request.user
    student = Student.objects.filter(application_number=user.username).first()

    if not student:
        return render(request, "error.html", {"message": "Student profile not found."})

    last_semester = student.get_last_semester()
    last_gpa = student.calculate_gpa_for_semester(last_semester) if last_semester else None

    # Get registered courses for current semester
    registered_courses = RegisteredCourse.objects.filter(
        student=student,
        semester=student.semester
    ).select_related('course')

    # Calculate total units from registered courses
    total_units = sum(reg_course.course.unit for reg_course in registered_courses)
    total_course = registered_courses.count()
    
    # Calculate units remaining (max 24 units)
    units_remaining = 24 - total_units if total_units <= 24 else 0

    context = {
        'student': student,
        'total_course': total_course,
        'total_unit': total_units,
        'units_remaining': units_remaining,
        'registered_courses': registered_courses,
        'last_gpa': last_gpa,
        'last_semester': last_semester,
        'update_profile_picture_url': reverse('update_profile_picture'),
        'upcoming_deadlines': [],  # Add your deadlines logic here
        'recent_announcements': [],  # Add your announcements logic here
    }

    return render(request, "student_portal.html", context)


def student_biodata(request):
    user = request.user  # Get the logged-in user
    try:
        student = Student.objects.get(application_number=user.username)
    except Student.DoesNotExist:
        student = None  # If student is not found, avoid errors

    return render(request, "student_biodata.html", {"student": student})


def CourseRegistration(request):
    user = request.user  # Get the logged-in user
    student = Student.objects.filter(application_number=user.username).first()
    courses = Course.objects.filter(
        department=student.department,
        semester=student.semester,
    )  # Fetch their application

    return render (request, 'portal_course_registration.html', {"courses": courses, "student": student})

def submit_registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_ids = data.get("courses", [])
            student = Student.objects.get(application_number=request.user.username)

            # Assuming student.semester is already set
            semester = student.semester

            # Register selected courses
            for course_id in course_ids:
                course = Course.objects.get(id=course_id)
                RegisteredCourse.objects.get_or_create(
                    student=student,
                    course=course,
                    semester=semester  # ✅ include semester
                )

            return JsonResponse({"success": True, "message": "Courses registered successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})


def registered_courses(request):
    user = request.user
    student = Student.objects.filter(application_number=user.username).first()
    
    if not student:
        return render(request, "error.html", {"message": "Student profile not found."})

    registered_courses = RegisteredCourse.objects.filter(
    student=student,
    semester=student.semester
)


    return render(request, "portal_registered_courses.html", {
        "registered_courses": registered_courses,
        "student": student
    })

def headline_news(request):
    headlines = Headline.objects.all()
    return render(request, "portal-news.html", {"headlines": headlines})



def apply_for_admission(request):
    form = ApplicationForm()
    
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save()
            return redirect('application_success', application.application_number, application.surname)
    
    # Get all LGAs grouped by state for client-side filtering
    all_lgas = {}
    for state in State.objects.all():
        lgas = Lga.objects.filter(state_of_origin=state).order_by('name')
        all_lgas[state.id] = [{'id': lga.id, 'name': lga.name} for lga in lgas]
    
    # Debug: Print the all_lgas data
    print("All LGAs Data:", all_lgas)
    
    return render(request, 'apply.html', {
        'form': form,
        'all_lgas_json': json.dumps(all_lgas)  # Convert to JSON for JavaScript
    })





def application_success(request, application_number, surname):
    return render(request, 'application_success.html', {
        'application_number': application_number,
        'surname': surname
    })

def admission_success(request, application_number, surname):
    return render(request, 'admission_success.html', {
        'application_number': application_number,
        'surname': surname
    })



def get_lgas(request):
    """Returns LGAs based on the selected state."""
    state_id = request.GET.get("state_id")  # ✅ Get state ID from AJAX request
    if state_id:
        lgas = Lga.objects.filter(state_id=state_id).values("id", "name")
        return JsonResponse({"lgas": list(lgas)})
    return JsonResponse({"lgas": []})  # ✅ Return empty list if no state is selected


def get_departments(request):
    """Returns departments based on the selected school."""
    school_id = request.GET.get("school_id")  # ✅ Get school ID from AJAX request
    if school_id:
        departments = Department.objects.filter(school_id=school_id).values("id", "name")
        return JsonResponse({"departments": list(departments)})
    return JsonResponse({"departments": []})  # ✅ Return empty list if no school is selected

def get_lgas(request):
    state_id = request.GET.get('state_id')
    
    if not state_id:
        return JsonResponse({'error': 'No state ID provided'}, status=400)
    
    try:
        lgas = Lga.objects.filter(state_of_origin_id=state_id).order_by('name')
        lga_list = [{'id': lga.id, 'name': lga.name} for lga in lgas]
        
        print(f"Found {len(lga_list)} LGAs for state {state_id}")
        print(f"First few LGAs: {lga_list[:3]}")
        
        return JsonResponse({'lgas': lga_list})
    except Exception as e:
        print(f"Error in get_lgas: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    


def Notification_Page(request):
    user = request.user
    notifications = Notification.objects.all()
    student = Student.objects.filter(application_number=user.username).first()

    return render(request, 'portal_notification.html', {'notifications':notifications, 'student':student})

@require_http_methods(["GET", "POST"])
def View_Notification(request, Notification_id):
    user = request.user
    student = Student.objects.filter(application_number=user.username).first()
    notification = get_object_or_404(Notification, id=Notification_id)

    # Handle POST request to mark as read
    if request.method == 'POST':
        if not notification.read:
            notification.read = True
            notification.read_at = timezone.now()
            notification.save()
        return JsonResponse({'success': True})

    # Handle GET request (normal page load)
    return render(request, 'portal_notification_page.html', {
        'notification': notification,
        'student': student,
    })