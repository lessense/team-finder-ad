from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

from core.validators import validate_github_url, validate_phone_format

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Пароль")
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Подтверждение пароля"
    )

    class Meta:
        model = User
        fields = ["name", "surname", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label="Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label="Пароль")


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "surname": forms.TextInput(attrs={"class": "form-control"}),
            "about": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "github_url": forms.URLInput(attrs={"class": "form-control"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            validate_phone_format(phone)
            if phone.startswith("8"):
                phone = "+7" + phone[1:]
        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url:
            validate_github_url(url)
        return url


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Старый пароль"
        self.fields["new_password1"].label = "Новый пароль"
        self.fields["new_password2"].label = "Подтверждение пароля"
