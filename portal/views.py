from django.shortcuts import render, redirect
from .forms import ApplicationForm
from .models import Application, Course, State, Lga  # Ensure you import your model
from django.http import JsonResponse
import json

# Create your views here.


def home(request):
    return render(request, 'home.html')

def application_view(request):
    applications = Application.objects.all()
    return render(request, 'application-portal.html', {'applications': applications})







def apply_for_admission(request):
    form = ApplicationForm()
    
    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            return redirect('application-success', application.application_number, application.surname)
    
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