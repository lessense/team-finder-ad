from django.urls import path

from projects import views
from projects import views_favorites

app_name = "projects"

urlpatterns = [
    path("list/", views.project_list_view, name="project_list"),
    path("<int:pk>/", views.project_detail_view, name="project_detail"),
    path("create-project/", views.create_project_view, name="create_project"),
    path("<int:pk>/edit/", views.edit_project_view, name="edit_project"),
    path("<int:pk>/complete/", views.complete_project_view, name="complete_project"),
    path(
        "<int:pk>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle_participate",
    ),
    # ДЛЯ ВАРИАНТА 1:
    path(
        "<int:pk>/toggle-favorite/",
        views_favorites.toggle_favorite,
        name="toggle_favorite",
    ),
    path("favorites/", views_favorites.favorites_list, name="favorites_list"),
]
