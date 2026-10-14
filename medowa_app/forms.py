from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com', 'autocomplete': 'email'}),
    )
    username = forms.CharField(
        min_length=4,
        widget=forms.TextInput(attrs={'placeholder': 'applefan', 'autocomplete': 'username'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a strong password', 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat your password', 'autocomplete': 'new-password'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'username'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'autocomplete': 'current-password'}),
    )


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Full name', 'autocomplete': 'name'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com', 'autocomplete': 'email'}),
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Street address', 'rows': 3, 'autocomplete': 'street-address'}),
    )
    city = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={'placeholder': 'City', 'autocomplete': 'address-level2'}),
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Postal code', 'autocomplete': 'postal-code'}),
    )
