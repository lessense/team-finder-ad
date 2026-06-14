from django.db.models import Prefetch

from projects.models import Project


def get_projects_with_related():
    """Возвращает queryset проектов с оптимизацией связанных данных."""
    return Project.objects.select_related("owner").prefetch_related(
        Prefetch("participants")
    )
