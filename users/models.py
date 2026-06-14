import random
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from core.constants import (
    MAX_PHONE_LENGTH,
    MAX_USER_ABOUT_LENGTH,
    MAX_USER_NAME_LENGTH,
    MAX_USER_SURNAME_LENGTH,
)
from users.managers import UserManager

# Константы для аватара
AVATAR_SIZE = (200, 200)
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_COLOR = (255, 255, 255)
AVATAR_COLORS = [
    (73, 109, 137),  # Soft blue
    (76, 114, 92),  # Soft green
    (156, 110, 86),  # Soft brown
    (114, 86, 128),  # Soft purple
    (179, 102, 79),  # Soft orange
    (82, 119, 112),  # Soft teal
]


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    name = models.CharField(max_length=MAX_USER_NAME_LENGTH, verbose_name="Имя")
    surname = models.CharField(
        max_length=MAX_USER_SURNAME_LENGTH, verbose_name="Фамилия"
    )
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Аватар"
    )
    phone = models.CharField(
        max_length=MAX_PHONE_LENGTH,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телефон",
    )
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=MAX_USER_ABOUT_LENGTH, blank=True, verbose_name="О себе"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
    )

    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = self.generate_avatar()
        super().save(*args, **kwargs)

    def generate_avatar(self):
        """Генерирует аватар с первой буквой имени"""
        bg_color = random.choice(AVATAR_COLORS)

        img = Image.new("RGB", AVATAR_SIZE, bg_color)
        draw = ImageDraw.Draw(img)

        letter = self.name[0].upper() if self.name else "?"
        try:
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (AVATAR_SIZE[0] - text_width) // 2
        y = (AVATAR_SIZE[1] - text_height) // 2

        draw.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=f"avatar_{self.email}.png")
