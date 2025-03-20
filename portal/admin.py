from django.contrib import admin
from .models import School, Department, Application, State, Lga, Student
# Register your models here.


admin.site.register(School)
admin.site.register(Department)
admin.site.register(Application)
admin.site.register(State)
admin.site.register(Lga)
admin.site.register(Student)