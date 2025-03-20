from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now

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

# ------------------ SCHOOL & COURSE MODELS ------------------

class School(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

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
    is_approved = models.BooleanField(default=False)  # New field to track approval

    def save(self, *args, **kwargs):
        if not self.application_number:
            last_entry = Application.objects.order_by('-id').first()
            new_number = int(last_entry.application_number[5:]) + 1 if last_entry else 1
            self.application_number = f"A2025{new_number:03d}"

        super().save(*args, **kwargs)

    def approve(self):
        """Transfers application data to Student model upon approval but keeps the application record."""
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
        )
        
        self.is_approved = True  # Mark as approved instead of deleting
        self.save()

    def __str__(self):
        return f"{self.surname} ({self.application_number})"

# ------------------ AUTOMATIC USER CREATION ------------------

@receiver(post_save, sender=Application)
def create_application_user(sender, instance, created, **kwargs):
    if created:
        user, created = User.objects.get_or_create(
            username=instance.application_number,
            defaults={
                "first_name": instance.first_name,
                "last_name": instance.surname,
                "password": make_password(instance.surname),  # Store hashed password
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

    def __str__(self):
        return f"{self.surname} ({self.application_number})"
    


class AcademicSession(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensuring session names are unique
    
    def __str__(self):
        return self.name
    

    class Meta:
      ordering = ["-id"]  # Orders by newest first