from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Banner, Category, Product

INPUT = 'dashInput'
CHECK = 'dashCheck'


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


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'image', 'image_file', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. iPhone 16 Pro'}),
            'category': forms.Select(attrs={'class': INPUT}),
            'price': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01', 'placeholder': '0.00'}),
            'description': forms.Textarea(attrs={'class': INPUT, 'rows': 5, 'placeholder': 'Describe the product'}),
            'image': forms.URLInput(attrs={'class': INPUT, 'placeholder': 'https://example.com/image.jpg'}),
            'image_file': forms.ClearableFileInput(attrs={'class': INPUT}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECK}),
        }
        labels = {
            'image': 'Image URL (optional)',
            'image_file': 'Upload image (optional)',
            'is_active': 'Visible on the storefront',
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. iPad'}),
            'slug': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. ipad'}),
        }
        help_texts = {
            'slug': 'Lowercase identifier used in the storefront filter links.',
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'link_url', 'image', 'image_file', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Banner headline'}),
            'subtitle': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Supporting line'}),
            'link_url': forms.TextInput(attrs={'class': INPUT, 'placeholder': '/ or /?category=mac'}),
            'image': forms.URLInput(attrs={'class': INPUT, 'placeholder': 'https://...'}),
            'image_file': forms.ClearableFileInput(attrs={'class': INPUT}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECK}),
        }


class StaffUserForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        label='Password',
        widget=forms.PasswordInput(attrs={'class': INPUT, 'autocomplete': 'new-password', 'placeholder': 'Set a password'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. applefan'}),
            'email': forms.EmailInput(attrs={'class': INPUT, 'placeholder': 'name@example.com'}),
            'first_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Last name'}),
            'is_staff': forms.CheckboxInput(attrs={'class': CHECK}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECK}),
        }
        labels = {
            'is_staff': 'Administrator access',
            'is_active': 'Account active',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.fields['password'].required = True
            self.fields['password'].help_text = 'Choose a password for this new user.'
        else:
            self.fields['password'].help_text = 'Leave blank to keep the current password.'

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
