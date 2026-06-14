from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from core.constants import PAGE_SIZE
from core.services import paginate_queryset
from users.forms import LoginForm, ProfileEditForm, RegistrationForm
from users.models import User


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
            form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


def user_detail_view(request, pk):
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
    users = User.objects.select_related().all().order_by("-date_joined")

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
            users = User.objects.filter(
                participated_projects__in=my_projects
            ).distinct()

    page_obj = paginate_queryset(request, users, PAGE_SIZE)
    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "active_filter": active_filter,
            "query_prefix": f"filter={active_filter}&" if active_filter else "",
        },
    )
