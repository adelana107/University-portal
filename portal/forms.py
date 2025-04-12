from django import forms
from .models import Application, Department, State, Lga

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'surname', 'first_name', 'other_name', 'email', 'phone_number', 
            'address', 'state_of_origin', 'local_government', 
            'date_of_birth', 'school', 'department', 'profile_picture', 'academic_session'
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
                self.fields['Department'].queryset = Department.objects.filter(school=self.instance.school)
            
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


class ApplicantLoginForm(forms.Form):
    application_number = forms.CharField(label="Application Number", max_length=20)
    surname = forms.CharField(label="Surname", widget=forms.PasswordInput)


class StudentLoginForm(forms.Form):
    application_number = forms.CharField(label="Application Number", max_length=20)
    surname = forms.CharField(label="Surname", widget=forms.PasswordInput)
