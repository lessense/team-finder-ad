from django.contrib import admin
from projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at", "participants_count")
    list_filter = ("status", "created_at")
    search_fields = ("name", "owner__email", "owner__name", "owner__surname")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Основная информация", {"fields": ("name", "description", "owner", "status")}),
        ("Ссылки и участники", {"fields": ("github_url", "participants")}),
        ("Даты", {"fields": ("created_at",)}),
    )

    def participants_count(self, obj):
        return obj.participants.count()

    participants_count.short_description = "Количество участников"
