from django.urls import path
from .views import crm_dashboard, applicant_list, edit_application, student_list, edit_student, view_applicant, approve_application, revoke_application, Crmlogin, view_student



urlpatterns = [
  
    path('applicant/', applicant_list, name='applicant_list'),
    path('student/', student_list, name = 'student_list' ),
    path('edit-student/<int:student_id>/', edit_student, name='edit_student'),
    path('edit_application/<int:application_id>/', edit_application, name= 'edit_application'),
    path('applications/view/<int:application_id>/', view_applicant, name='view_applicant'),
    path('student-profile/view/<int:student_id>/', view_student, name='view_student'),

    path("approve/<int:application_id>/", approve_application, name="approve_application"),
    path('revoke-application/<int:application_id>/', revoke_application, name='revoke_application'),
    path("crm/login/", Crmlogin, name="crm_login"),
    path("crm/dashboard/", crm_dashboard, name="crm_dashboard"),

   
]