from django.urls import path
from .views import dashboard, applicant_list, edit_application, student_list, edit_student, view_applicant



urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('applicant/', applicant_list, name='applicant_list'),
    path('student/', student_list, name = 'student_list' ),
    path('edit-student/<int:student_id>/', edit_student, name='edit_student'),
    path('edit_application/<int:application_id>/', edit_application, name= 'edit_application'),
    path('applications/view/<int:application_id>/', view_applicant, name='view_applicant'),

   
]