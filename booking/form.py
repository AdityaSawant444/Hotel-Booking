from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'guest_email', 'guest_phone', 'num_adults', 'num_children','check_in','check_out','num_rooms']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter guest name'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'value': '0'}),
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
        }

class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'guest_email', 'guest_phone', 'num_adults', 'num_children','check_in','check_out']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
        }

class BookingDeleteForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'guest_email', 'guest_phone', 'num_adults', 'num_children','check_in','check_out']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'num_adults': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'num_children': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'num_rooms': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
        }

