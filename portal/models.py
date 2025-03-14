from django.db import models

class State(models.Model):  # Use PascalCase for model names
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