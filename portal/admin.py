from django.contrib import admin
from .models import School, Course, Application, State, Lga
# Register your models here.


admin.site.register(School)
admin.site.register(Course)
admin.site.register(Application)
admin.site.register(State)
admin.site.register(Lga)