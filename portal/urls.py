from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from . import views
from .views import apply_for_admission,  applicant_login, applicant_profile, application_success, get_lgas, get_departments, student_portal, admission_success, student_biodata, student_login, CourseRegistration

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/',apply_for_admission, name='apply'),
    path("get_lgas/", get_lgas, name="get_lgas"),  # ✅ Ensure this URL exists
    path("get_departments/",get_departments, name="get_departments"),
    path("login/", applicant_login, name="applicant_login"),
    path("applicant-profile/", applicant_profile, name="application_profile"),
    path("student-portal-login/", student_login, name="student_login"),
    path("student-portal/", student_portal, name="student_portal"),
    path("student-biodata/", student_biodata, name="student_biodata"),
    path('course-registration/', CourseRegistration, name='course_registration'),
    path("logout/", LogoutView.as_view(next_page="applicant_login"), name="logout"), 
    path('application-success/<str:application_number>/<str:surname>/', application_success, name='application_success'),
    path('admission-success/<str:application_number>/<str:surname>/', admission_success, name='admission_success'), 
]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
