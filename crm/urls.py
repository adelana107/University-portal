from django.urls import path
from .views import (
    crm_dashboard, applicant_list, edit_application, student_list, 
    edit_student, view_applicant, approve_application, revoke_application, 
    Crmlogin, view_student, move_to_new_semester, move_to_previous_semester, move_semester_confirmationPage,
    semester_success, reverse_semester_confirmationPage, semester_reverse_success
)

urlpatterns = [
    # Applicant URLs
    path('applicant/', applicant_list, name='applicant_list'),
    path('applications/view/<int:application_id>/', view_applicant, name='view_applicant'),
    path('edit-application/<int:application_id>/', edit_application, name='edit_application'),
    path("approve/<int:application_id>/", approve_application, name="approve_application"),
    path('revoke-application/<int:application_id>/', revoke_application, name='revoke_application'),

    # Student URLs
    path('student/', student_list, name='student_list'),
    path('student-profile/view/<int:student_id>/', view_student, name='view_student'),
    path('edit-student/<int:student_id>/', edit_student, name='edit_student'),

    # CRM Authentication & Dashboard
    path("crm/login/", Crmlogin, name="crm_login"),
    path("crm/dashboard/", crm_dashboard, name="crm_dashboard"),

    # Semester Management
    path("move-semester/", move_to_new_semester, name="move_semester"),
    path("confirm-move/", move_semester_confirmationPage, name="confirmation_page"),
    path("confirm-reverse/",reverse_semester_confirmationPage, name="reverse_confirmation_page"),
    path("semester-success/", semester_success, name="semester_success"),
    path("semester-reverse-success/", semester_reverse_success, name="reverse_semester_success"),
    path("move-to-previous-semester/", move_to_previous_semester, name="reverse_semester"),

    
    
]
