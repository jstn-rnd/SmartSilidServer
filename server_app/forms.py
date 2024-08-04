from django import forms
from .models import Blacklist

from .models import Whitelist, Blacklist

class WhitelistForm(forms.ModelForm):
    class Meta:
        model = Whitelist
        fields = ['url']

class BlacklistForm(forms.ModelForm):
    class Meta:
        model = Blacklist
        fields = ['url']
     