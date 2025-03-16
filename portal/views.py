from django.shortcuts import render, redirect, get_object_or_404
from .forms import ApplicationForm
from .models import Application, Course, State, Lga  # Ensure you import your model
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
                return redirect("profile")  # Redirect to profile page
            else:
                return render(request, "login.html", {"form": form, "error": "Invalid application number or surname."})
    else:
        form = ApplicantLoginForm()

    return render(request, "login.html", {"form": form})



def home(request):
    return render(request, 'home.html')




@login_required
def applicant_profile(request):
    user = request.user  # Get the logged-in user
    applications = Application.objects.filter(application_number=user.username)  # Fetch their application

    return render(request, "profile.html", {"applications": applications})



def apply_for_admission(request):
    form = ApplicationForm()
    
    if request.method == "POST":
        form = ApplicationForm(request.POST)
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


def get_courses(request):
    school_id = request.GET.get('school_id')

    if school_id:
        courses = Course.objects.filter(school_id=school_id).values('id', 'name')
        return JsonResponse({'courses': list(courses)})

    return JsonResponse({'error': 'Invalid request'}, status=400)

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