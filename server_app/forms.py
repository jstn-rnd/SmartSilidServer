from django import forms
from .models import Blacklist
from django import forms

from .models import Whitelist, Blacklist, Schedule

class WhitelistForm(forms.ModelForm):
    class Meta:
        model = Whitelist
        fields = ['url']

class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = ['url']

class ScheduleForm(forms.ModelForm):
    start_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Use 12-hour format with AM/PM
        widget=forms.TimeInput(format='%I:%M %p')
    )
    end_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Use 12-hour format with AM/PM
        widget=forms.TimeInput(format='%I:%M %p')
    )

    class Meta:
        model = Schedule
        fields = ['subject', 'start_time', 'end_time', 'weekdays', 'rfids']
