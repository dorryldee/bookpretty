from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.utils import timezone 
from django.contrib.auth import get_user_model
from .models import  Appointment, Client, ContactMessage, Service

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','first_name','email','password1','password2']

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True, max_length=150)
    phone = forms.CharField(required=False, max_length=30)

    class Meta:
        model = User
        # username + password fields are included via UserCreationForm
        fields = ("username", "email", "name", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        # store email on user model if it has the field (default auth user has email)
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
            # create linked Client profile
            Client.objects.create(
                user=user,
                name=self.cleaned_data.get("name", user.username),
                email=self.cleaned_data.get("email", ""),
                phone=self.cleaned_data.get("phone", ""),
            )
        return user

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'dob', 'notes', 'avatar', 'is_active'
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        qs = Client.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already used by another client.")
        return email

class ReviewForm(forms.Form):
    review_notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2}), label="Notes (optional)")

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']   
        

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'duration']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'duration': forms.TimeInput(attrs={'type': ''}),
        }
        
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
   
       
