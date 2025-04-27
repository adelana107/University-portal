from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),

    # Admission & Application
    path('apply/', views.apply_for_admission, name='apply'),
    path('application-success/<str:application_number>/<str:surname>/', views.application_success, name='application_success'),
    path('admission-success/<str:application_number>/<str:surname>/', views.admission_success, name='admission_success'),

    # Authentication
    path('login/', views.applicant_login, name='applicant_login'),
    path('logout/', LogoutView.as_view(next_page="applicant_login"), name="logout"),
    
    # Applicant Profile
    path('applicant-profile/', views.applicant_profile, name='application_profile'),

    # Student Portal
    path('student-portal-login/', views.student_login, name='student_login'),
    path('student-portal/', views.student_portal, name='student_portal'),
    path('student-biodata/', views.student_biodata, name='student_biodata'),

    # Course Registration
    path('course-registration/', views.CourseRegistration, name='course_registration'),
    path('submit-registration/', views.submit_registration, name='submit_registration'),
    path('registered-courses/', views.registered_courses, name='registered_courses'),

    # AJAX Endpoints
    path('get_lgas/', views.get_lgas, name='get_lgas'),
    path('get_departments/', views.get_departments, name='get_departments'),

    path('headline-news/', views.headline_news, name='headline_news'),

    #notifications
    path('student-notifications/', views.Notification_Page, name='notifications'),
    path('student-notification/<int:Notification_id>/',  views.View_Notification,  name='notification_page'),
    path('mark-notification-read/<int:notification_id>/',  views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
   

    path('update-profile-picture/', views.update_profile_picture, name='update_profile_picture'),

    
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
