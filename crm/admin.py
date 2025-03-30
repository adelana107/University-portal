from django.contrib import admin
from portal.models import Application,Student, Notification
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html

# Register your models here.
if not admin.site.is_registered(Application):
    admin.site.register(Application)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("surname", "first_name", "application_number", "email", "phone_number", "department")
    search_fields = ("surname", "application_number", "email")
    list_filter = ("school", "department")


    @admin.display(description="Approval")
    def approve_button(self, obj):
        """Displays the approval button in the CRM admin panel."""
        if not obj.is_approved:
            return format_html('<a class="button btn btn-success" href="approve/{}/">✅ Approve</a>', obj.id)
        return "✔️ Approved"


    def get_urls(self):
        """Defines a custom URL for approving applications in CRM."""
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:app_id>/', self.approve_application, name="approve_application"),
        ]
        return custom_urls + urls

    def approve_application(self, request, app_id):
        """Handles the approval process when the button is clicked."""
        application = Application.objects.get(id=app_id)
        application.approve()
        application.is_approved = True
        application.save()
        self.message_user(request, f"✅ {application.surname} has been approved as a student!")
        return redirect("..")  # Redirect to the previous page
    

