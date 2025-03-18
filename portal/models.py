from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save, post_delete
from django.utils.timezone import now





class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Lga(models.Model):
    name = models.CharField(max_length=100)
    state_of_origin = models.ForeignKey(State, on_delete=models.CASCADE, related_name="lgas")

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=10, unique=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True, default="profile_pics/default-profile.png")
    created_at = models.DateTimeField(default=now, editable=True)

    
    def save(self, *args, **kwargs):
        if not self.application_number:
            last_entry = Application.objects.order_by('-id').first()
            if last_entry and last_entry.application_number:
                last_number = int(last_entry.application_number[5:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.application_number = f"A2025{new_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.surname} ({self.application_number})"

# Automatically create a user when an application is created
@receiver(post_save, sender=Application)
def create_application_user(sender, instance, created, **kwargs):
    if created:
        user, created = User.objects.get_or_create(
            username=instance.application_number,
            defaults={
                "first_name": instance.first_name,
                "last_name": instance.surname,
                "password": make_password(instance.surname),  # Hash the password
            }
        )
        if created:
            print(f"✅ User created: {user.username} with hashed password")
        else:
            print(f"⚠️ User already exists: {user.username}")

# Automatically delete the user when an application is deleted
@receiver(post_delete, sender=Application)
def delete_application_user(sender, instance, **kwargs):
    try:
        user = User.objects.get(username=instance.application_number)
        if not user.is_staff:  # Ensure admin users are not deleted
            user.delete()
            print(f"🗑️ User deleted: {instance.application_number}")
        else:
            print(f"⚠️ Skipping deletion for admin user: {instance.application_number}")
    except User.DoesNotExist:
        print(f"⚠️ No user found for deletion: {instance.application_number}")




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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=10, unique=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True, default="profile_pics/default-profile.png")
    created_at = models.DateTimeField(default=now, editable=True)


    def __str__(self):
        return f"{self.surname} ({self.application_number})"


    

