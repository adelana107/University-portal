from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('application-portal/', views.application_view, name='application'),
    path('apply/', views.apply_for_admission, name='apply'),
    path('application-success/<str:application_number>/<str:surname>/', views.application_success, name='application-success'),
    path('get-courses/', views.get_courses, name='get_courses'),
   path('get-lgas/', views.get_lgas, name='get_lgas'),    
]    