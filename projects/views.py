import http

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.constants import STATUS_CLOSED, STATUS_OPEN
from core.services import paginate_queryset
from projects.forms import ProjectForm
from projects.models import Project
from projects.services import get_projects_with_related


def project_list_view(request):
    projects = get_projects_with_related().order_by("-created_at")
    page_obj = paginate_queryset(request, projects)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, pk):
    project = get_object_or_404(get_projects_with_related(), pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:project_detail", pk=project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_detail", pk=project.pk)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True},
    )


@login_required
def complete_project_view(request, pk):
    project = Project.objects.filter(pk=pk, owner=request.user).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=http.HTTPStatus.NOT_FOUND,
        )

    if project.status == STATUS_OPEN:
        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})

    return JsonResponse(
        {"status": "error", "message": "Проект уже закрыт"},
        status=http.HTTPStatus.BAD_REQUEST,
    )


@login_required
def toggle_participate_view(request, pk):
    project = Project.objects.filter(pk=pk).first()
    if not project:
        return JsonResponse(
            {"status": "error", "message": "Проект не найден"},
            status=http.HTTPStatus.NOT_FOUND,
        )

    is_participant = project.participants.filter(pk=request.user.pk).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "joined": not is_participant})
