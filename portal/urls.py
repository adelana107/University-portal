from django.urls import path
from . import views
from .views import applicant_login, applicant_profile
from django.contrib.auth.views import LogoutView
from .views import application_success



urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply_for_admission, name='apply'),
    path('get-courses/', views.get_courses, name='get_courses'),
    path('get-lgas/', views.get_lgas, name='get_lgas'),
    path("login/", applicant_login, name="applicant_login"),
    path("profile/", applicant_profile, name="profile"),
    path("logout/", LogoutView.as_view(next_page="applicant_login"), name="logout"), 
    path('application-success/<str:application_number>/<str:surname>/', application_success, name='application_success'), 
]    