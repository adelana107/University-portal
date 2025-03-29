from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now


# ------------------ CATEGORY MODEL ------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ------------------ YEAR & SEMESTER MODELS ------------------
class Year(models.Model):
    number = models.IntegerField(unique=True)  # Example: 1, 2, 3, 4

    def __str__(self):
        return f"Year {self.number}"


class Semester(models.Model):
    name = models.CharField(max_length=20)  # "First" or "Second"
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="semesters")

    class Meta:
        unique_together = ("name", "year")  # Ensure each year has only one "First" & "Second"

    def __str__(self):
        return f"{self.name} Semester - Year {self.year.number}"


# ------------------ SCHOOL & DEPARTMENT MODELS ------------------
class School(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="departments")

    def __str__(self):
        return self.name


# ------------------ COURSE MODELS ------------------
class Course(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    unit = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="courses")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.title


class RegisteredCourse(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="courses_registered")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("student", "course")  # Ensures students can't register the same course twice

    def __str__(self):
        return f"{self.student.surname} - {self.course.title}"


# ------------------ STATE & LGA MODELS ------------------
class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Lga(models.Model):
    name = models.CharField(max_length=100)
    state_of_origin = models.ForeignKey(State, on_delete=models.CASCADE, related_name="lgas")

    def __str__(self):
        return self.name


# ------------------ HELPER FUNCTION ------------------
def get_default_semester():
    return Semester.objects.first()  # Returns `None` if no semester exists


# ------------------ APPLICATION MODEL ------------------
class Application(models.Model):
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=100)
    state_of_origin = models.ForeignKey(State, on_delete=models.CASCADE)
    local_government = models.ForeignKey(Lga, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=10, unique=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True, default="profile_pics/default-profile.png")
    created_at = models.DateTimeField(default=now, editable=True)
    academic_session = models.ForeignKey("AcademicSession", on_delete=models.CASCADE, related_name="applications")
    is_approved = models.BooleanField(default=False)  # Tracks approval status
    year = models.ForeignKey(Year, default=1, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, default=get_default_semester)

    def save(self, *args, **kwargs):
        if not self.application_number:
            count = Application.objects.count() + 1  # Ensure uniqueness
            self.application_number = f"A2025{count:03d}"
        super().save(*args, **kwargs)

    def approve(self):
        """Transfers application data to Student model upon approval."""
        Student.objects.create(
            surname=self.surname,
            first_name=self.first_name,
            other_name=self.other_name,
            email=self.email,
            phone_number=self.phone_number,
            address=self.address,
            state_of_origin=self.state_of_origin,
            local_government=self.local_government,
            date_of_birth=self.date_of_birth,
            school=self.school,
            department=self.department,
            application_number=self.application_number,
            profile_picture=self.profile_picture,
            academic_session=self.academic_session,
            year=self.year,
            semester=self.semester
        )

        # Create User for Student
        User.objects.get_or_create(
            username=self.application_number,
            defaults={
                "first_name": self.first_name,
                "last_name": self.surname,
                "password": make_password(self.surname),
            }
        )

        self.is_approved = True
        self.save()

    def __str__(self):
        return f"{self.surname} ({self.application_number})"


# ------------------ AUTOMATIC USER CREATION ------------------
@receiver(post_save, sender=Application)
def create_application_user(sender, instance, created, **kwargs):
    if created:
        User.objects.get_or_create(
            username=instance.application_number,
            defaults={
                "first_name": instance.first_name,
                "last_name": instance.surname,
                "password": make_password(instance.surname),
            }
        )


# ------------------ STUDENT MODEL ------------------
class Student(models.Model):
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11)
    address = models.CharField(max_length=100)
    state_of_origin = models.ForeignKey(State, on_delete=models.CASCADE)
    local_government = models.ForeignKey(Lga, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=10, unique=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True, default="profile_pics/default-profile.png")
    academic_session = models.ForeignKey("AcademicSession", on_delete=models.CASCADE, related_name="students")
    created_at = models.DateTimeField(default=now, editable=True)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.surname} ({self.application_number})"


# ------------------ ACADEMIC SESSION MODEL ------------------
class AcademicSession(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["-id"]  # Orders by newest first

    def __str__(self):
        return self.name


# ------------------ HEADLINE MODEL ------------------
class Headline(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to="news_images/", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
