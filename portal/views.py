from django.shortcuts import render, redirect, get_object_or_404
from .forms import ApplicationForm, StudentLoginForm
from .models import Application, Department, State, Lga, Student, Course  # Ensure you import your model
from django.http import JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .forms import ApplicantLoginForm

# Create your views here.


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

    return render(request, "student_portal.html", {"student": student})

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
    courses = Course.objects.all()  # Fetch their application

    return render (request, 'portal_course_registration.html', {"courses": courses, "student": student})


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
    

