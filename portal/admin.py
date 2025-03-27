from django.contrib import admin
from .models import School, Department, Application, State, Lga, Student, AcademicSession, Year, Semester, Course, RegisteredCourse
# Register your models here.


admin.site.register(School)
admin.site.register(Department)
admin.site.register(Application)
admin.site.register(State)
admin.site.register(Lga)
admin.site.register(Student)
admin.site.register(AcademicSession)
admin.site.register(Year)
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(RegisteredCourse)