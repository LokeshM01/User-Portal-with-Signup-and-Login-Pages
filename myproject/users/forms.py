from django import forms
from .models import Customer  # Import the Customer model from models.py

# Define the form for customer details
class CustomerForm(forms.ModelForm):
    country_code = forms.CharField(max_length=5, initial='+91') 
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})  # This will render the date picker
    )
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'birthdate', 'country_code']  # Fields to be included in the form

    # Custom validation for the phone number field
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number') 
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number