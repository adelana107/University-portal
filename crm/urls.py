from django.urls import path
from .views import dashboard, applicant_list, edit_application



urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('applicant/', applicant_list, name='applicant_list'),
    path("edit-application/<int:application_id>/", edit_application, name="edit_application"),
]