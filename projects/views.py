from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from core.constants import STATUS_OPEN, STATUS_CLOSED
from core.services import paginate_queryset
from projects.forms import ProjectForm
from projects.models import Project


def project_list_view(request):
    projects = Project.objects.select_related("owner").all().order_by("-created_at")
    page_obj = paginate_queryset(request, projects)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, pk):
    project = get_object_or_404(Project.objects.select_related("owner"), pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if project.status == STATUS_OPEN:
        project.status = STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": STATUS_CLOSED})
    return JsonResponse({"status": "error", "message": "Проект уже закрыт"}, status=400)


@login_required
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        joined = False
    else:
        project.participants.add(request.user)
        joined = True
    return JsonResponse({"status": "ok", "joined": joined})


def test_view(request):
    projects = Project.objects.all()
    return render(request, "projects/test.html", {"projects": projects})
