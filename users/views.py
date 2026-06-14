from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django import forms

from core.services import paginate_queryset
from users.models import User

from django.http import HttpResponse


def raw_user_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    return HttpResponse(f"""
    <h1>Проверка пользователя</h1>
    <p>ID: {user.id}</p>
    <p>Email: {user.email}</p>
    <p>Имя: {user.name}</p>
    <p>Фамилия: {user.surname}</p>
    <p>Суперпользователь: {user.is_superuser}</p>
    <hr>
    <a href="/users/{user.id}/">Обычная страница профиля</a>
    """)


# Формы прямо здесь, чтобы избежать проблем с импортами
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ["name", "surname", "email"]

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
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect("projects:project_list")
    else:
        form = RegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect("projects:project_list")
            else:
                form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


# ГЛАВНОЕ: ЭТА ФУНКЦИЯ ДОЛЖНА БЫТЬ ТОЧНО ТАКОЙ
def user_detail_view(request, pk):
    """Показывает профиль пользователя - ЛЮБОГО, даже если это не текущий пользователь"""
    user_detail = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user_detail": user_detail})


@login_required
def edit_profile_view(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:user_detail", pk=request.user.pk)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "users/change_password.html", {"form": form})


def participants_list_view(request):
    users = User.objects.all().order_by("-date_joined")

    # Фильтрация для варианта 1
    filter_type = request.GET.get("filter")
    active_filter = None

    if request.user.is_authenticated and filter_type:
        active_filter = filter_type

        if filter_type == "favorite_authors":
            favorite_projects = request.user.favorites.all()
            users = User.objects.filter(owned_projects__in=favorite_projects).distinct()
        elif filter_type == "my_participated_authors":
            participated = request.user.participated_projects.all()
            users = User.objects.filter(owned_projects__in=participated).distinct()
        elif filter_type == "my_projects_likers":
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(favorites__in=my_projects).distinct()
        elif filter_type == "my_projects_participants":
            my_projects = request.user.owned_projects.all()
            users = User.objects.filter(participated_projects__in=my_projects).distinct()

    page_obj = paginate_queryset(request, users)
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "active_filter": active_filter,
            "query_prefix": f"filter={active_filter}&" if active_filter else "",
        },
    )
