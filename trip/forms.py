from django import forms
from .models import TravelAgency

class TravelAgencyForm(forms.ModelForm):
    class Meta:
        model = TravelAgency
        fields = ['name', 'description', 'image', 'logo']