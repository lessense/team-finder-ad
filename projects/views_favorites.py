from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from projects.models import Project


@login_required
def toggle_favorite(request, pk):
    """Добавить/удалить проект из избранного"""
    project = get_object_or_404(Project, pk=pk)

    if request.user.favorites.filter(pk=pk).exists():
        request.user.favorites.remove(project)
        favorited = False
    else:
        request.user.favorites.add(project)
        favorited = True

    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def favorites_list(request):
    """Страница избранных проектов"""
    projects = request.user.favorites.all().order_by("-created_at")
    return render(request, "projects/favorite_projects.html", {"projects": projects})
