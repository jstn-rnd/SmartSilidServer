from django import forms

from django import forms

from .models import Schedule, User


class ScheduleForm(forms.ModelForm):
    start_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Use 12-hour format with AM/PM
        widget=forms.TimeInput(format='%I:%M %p')
    )
    end_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Use 12-hour format with AM/PM
        widget=forms.TimeInput(format='%I:%M %p')
    ) 

    faculty = forms.ModelChoiceField(
        queryset=User.objects.all(),  # Fetch all Faculty instances
        empty_label="Select Faculty",      # Optional: set a placeholder
        widget=forms.Select()               # Use a dropdown select widget
    )

    class Meta:
        model = Schedule
        fields = ['subject', 'start_time', 'end_time', 'weekdays', 'faculty']
