from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from . import views
from .views import applicant_login, applicant_profile, application_success, get_lgas, get_departments, student_portal, admission_success

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.apply_for_admission, name='apply'),
    path("get_lgas/", get_lgas, name="get_lgas"),  # ✅ Ensure this URL exists
    path("get_departments/",get_departments, name="get_departments"),


    path("login/", applicant_login, name="applicant_login"),
    path("profile/", applicant_profile, name="profile"),
    path("student-portal/", student_portal, name="student_portal"),
    path("logout/", LogoutView.as_view(next_page="applicant_login"), name="logout"), 
    path('application-success/<str:application_number>/<str:surname>/', application_success, name='application_success'),
    path('admission-success/<str:application_number>/<str:surname>/', admission_success, name='admission_success'), 
]

# ✅ Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
