from django import forms
from .models import Application, Course, State, Lga

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'surname', 'first_name', 'other_name', 'email', 'phone_number', 
            'address', 'state_of_origin', 'local_government', 
            'date_of_birth', 'school', 'course'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'state_of_origin': forms.Select(attrs={'class': 'form-select', 'id': 'id_state_of_origin'}),
            'local_government': forms.Select(attrs={'class': 'form-select', 'id': 'id_local_government'}),
        }

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        
        # Initialize course queryset
        self.fields['course'].queryset = Course.objects.none()
        
        # Initialize local_government queryset
        self.fields['local_government'].queryset = Lga.objects.none()

        # If form is being edited and already has data
        if self.instance.pk:
            if self.instance.school:
                self.fields['course'].queryset = Course.objects.filter(school=self.instance.school)
            
            if self.instance.state_of_origin:
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin=self.instance.state_of_origin)

        # If form is being submitted and has data
        if 'school' in self.data:
            try:
                school_id = int(self.data.get('school'))
                self.fields['course'].queryset = Course.objects.filter(school_id=school_id)
            except (ValueError, TypeError):
                pass

        if 'state_of_origin' in self.data:
            try:
                state_id = int(self.data.get('state_of_origin'))
                self.fields['local_government'].queryset = Lga.objects.filter(state_of_origin_id=state_id)
            except (ValueError, TypeError):
                pass