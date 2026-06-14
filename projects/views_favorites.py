import http

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from projects.models import Project


@login_required
def toggle_favorite(request, pk):
    """Добавить/удалить проект из избранного"""
    # Проверяем существование проекта через filter().first()
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=http.HTTPStatus.NOT_FOUND,
        )

    # Проверяем, есть ли проект в избранном
    is_favorited = request.user.favorites.filter(pk=pk).exists()

    if is_favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
def favorites_list(request):
    """Страница избранных проектов"""
    projects = request.user.favorites.all().order_by("-created_at")
    return render(request, "projects/favorite_projects.html", {"projects": projects})
