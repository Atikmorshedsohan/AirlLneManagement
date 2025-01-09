from django import forms
from .models import Registration

class PassengerForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        label="Username",
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        label="Password",
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        label="Confirm Password",
        required=True
    )

    class Meta:
        model = Registration
        fields = ['full_name', 'email', 'phone', 'nid', 'age', 'gender']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'nid': forms.TextInput(attrs={'placeholder': 'National ID'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'gender': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data
