from django import forms
from portal.models import Application, Department, School, State, Lga, Student, Headline, Category, Notification, Course, Grade



class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'surname', 'first_name', 'other_name', 'email', 'phone_number', 
            'address', 'state_of_origin', 'local_government', 
            'date_of_birth', 'school', 'department', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'state_of_origin': forms.Select(attrs={'class': 'form-select', 'id': 'id_state_of_origin'}),
            'local_government': forms.Select(attrs={'class': 'form-select', 'id': 'id_local_government'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap styling to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

        # Initialize course queryset
        self.fields['department'].queryset = Department.objects.none()
        self.fields['local_government'].queryset = Lga.objects.none()

        # If form is being edited and already has data
        if self.instance.pk:
            if self.instance.school:
                self.fields['department'].queryset = Department.objects.filter(school=self.instance.school)
            
            if self.instance.state_of_origin:
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin=self.instance.state_of_origin)

        # If form is being submitted and has data
        if 'school' in self.data:
            try:
                school_id = int(self.data.get('school'))
                self.fields['department'].queryset = Department.objects.filter(school_id=school_id)
            except (ValueError, TypeError):
                pass

        if 'state_of_origin' in self.data:
            try:
                state_id = int(self.data.get('state_of_origin'))
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin_id=state_id)
            except (ValueError, TypeError):
                pass



class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'surname', 'first_name', 'other_name', 'email', 'phone_number', 
            'address', 'state_of_origin', 'local_government', 
            'date_of_birth', 'school', 'department', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'state_of_origin': forms.Select(attrs={'class': 'form-select', 'id': 'id_state_of_origin'}),
            'local_government': forms.Select(attrs={'class': 'form-select', 'id': 'id_local_government'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply Bootstrap styling to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

        # Initialize course queryset
        self.fields['department'].queryset = Department.objects.none()
        self.fields['local_government'].queryset = Lga.objects.none()

        # If form is being edited and already has data
        if self.instance.pk:
            if self.instance.school:
                self.fields['department'].queryset = Department.objects.filter(school=self.instance.school)
            
            if self.instance.state_of_origin:
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin=self.instance.state_of_origin)

        # If form is being submitted and has data
        if 'school' in self.data:
            try:
                school_id = int(self.data.get('school'))
                self.fields['department'].queryset = Department.objects.filter(school_id=school_id)
            except (ValueError, TypeError):
                pass

        if 'state_of_origin' in self.data:
            try:
                state_id = int(self.data.get('state_of_origin'))
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin_id=state_id)
            except (ValueError, TypeError):
                pass            



class CrmLoginForm(forms.Form):
    email = forms.CharField(label="Email", max_length=20)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class HeadlineForm(forms.ModelForm):
    class Meta:
        model = Headline
        fields = ["title", "content", "image", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter headline title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Enter headline content"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["title", "message"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter notification title"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Enter notification content"}),
           
        }


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name"]  # Changed from "Name" to "name" to match model field
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter school name"
            }),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "school"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Enter department name"  # Changed from "school name" to be more accurate
            }),
            "school": forms.Select(attrs={  # Changed to Select since school is likely a ForeignKey
                "class": "form-control",
                "placeholder": "Select school"
            }),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial empty queryset for department if no school is selected
        if 'school' in self.data:
            try:
                school_id = int(self.data.get('school'))
                self.fields['department'].queryset = Department.objects.filter(school_id=school_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['department'].queryset = self.instance.school.department_set.order_by('name')
        else:
            self.fields['department'].queryset = Department.objects.none()


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['course'].queryset = Course.objects.none()

        if 'semester' in self.data:
            try:
                semester_id = int(self.data.get('semester'))
                self.fields['course'].queryset = Course.objects.filter(semester_id=semester_id).order_by('title')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['course'].queryset = self.instance.semester.courses.order_by('title')
