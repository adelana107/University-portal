from django.contrib import admin
from portal.models import Application

# Register your models here.
if not admin.site.is_registered(Application):
    admin.site.register(Application)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("surname", "first_name", "application_number", "email", "phone_number", "course")
    search_fields = ("surname", "application_number", "email")
    list_filter = ("school", "course")

