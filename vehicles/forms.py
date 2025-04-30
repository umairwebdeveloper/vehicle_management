from django import forms
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["reg_number", "make", "model", "year", "vin"]
        widgets = {
            "reg_number": forms.TextInput(attrs={"autofocus": True}),
        }
        help_texts = {
            "reg_number": "Enter your vehicle registration number to fetch details.",
        }