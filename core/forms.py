from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address, ProductionReport, ToyType, Toy, Review, ToyReview

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code', 'country']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_pic = forms.ImageField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'profile_pic']

class CustomToyForm(forms.Form):
    name = forms.CharField(max_length=100, label="Toy Name")
    specification = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe your dream toy...'}),
        label="Specification"
    )
    size = forms.ChoiceField(
        choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')],
        label="Size"
    )
    type = forms.ModelChoiceField(queryset=ToyType.objects.all(), label="Toy Type")


class ProductionReportForm(forms.ModelForm):
    class Meta:
        model = ProductionReport
        fields = ['toy', 'report_text']
        widgets = {
            'report_text': forms.Textarea(attrs={'placeholder': 'Describe quality, condition, packaging, etc...'})
        }

class ToyEditForm(forms.ModelForm):
    class Meta:
        model = Toy
        fields = ['name', 'type', 'picture', 'size', 'cost_of_production', 'rating', 'specification', 'price']
        widgets = {
            'specification': forms.Textarea(attrs={'rows': 3}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'step': 1,
                'placeholder': '1-5'
            }),
            'comments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your feedback...'})
        }

class ToyReviewForm(forms.ModelForm):
    class Meta:
        model = ToyReview
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1, 'max': 5, 'step': 1,
                'placeholder': '1-5'
            })
        }
