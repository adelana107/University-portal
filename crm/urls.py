from django.urls import path
from .views import (
    crm_dashboard, applicant_list, edit_application, student_list, 
    edit_student, view_applicant, approve_application, revoke_application, 
    Crmlogin, view_student, move_to_new_semester, move_to_previous_semester, move_semester_confirmationPage,
    semester_success, reverse_semester_confirmationPage, semester_reverse_success, Post_headline, Edit_headline, delete_headline,
    school_view, Notify_student, add_School, department_view, add_department, course_view, add_course,  load_departments, load_courses, add_grade, grade_list,
    edit_grade
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

    #headline Post
    path("headline/", Post_headline, name="Post_headline"),
    path("edit-headline/<int:headline_id>/", Edit_headline, name="edit_headline"),

    path('delete-headline/<int:headline_id>/', delete_headline, name='delete_headline'),

    #school view
    path("school-list/", school_view, name = "school_list"),

    #department view
    path("department-list/", department_view, name = "department_list" ),

    #Notification URLS

    path("notification/", Notify_student, name = "Notify_student" ),

    #school management
    path("add-school/", add_School, name = "add_school" ),

    #department management
    path("add-department/", add_department, name = "add_department" ),

    #course view
    path("course-list/", course_view, name = "course_list" ),

    #course management
    path("add-course/", add_course, name = "add_course" ),
    path('ajax/load-courses/', load_courses, name='ajax_load_courses'),


    #Grade Management
    path('add-grade/', add_grade, name='add_grade'),
    path('grades/', grade_list, name='grade_list'),
    path("edit-grade/<int:grade_id>/", edit_grade, name="edit_grade"),



    path('ajax/load-departments/', load_departments, name='ajax_load_departments'),
]