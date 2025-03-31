from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code', 'country']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'profile_pic']

class CustomToyForm(forms.Form):
    specification = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe your dream toy...'}),
        label="Your Toy Specification"
    )