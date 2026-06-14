from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

from core.constants import (
    MAX_USER_NAME_LENGTH,
    MAX_USER_SURNAME_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_USER_ABOUT_LENGTH,
)


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


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

    # Django auth поля
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="custom_user_set",
        related_query_name="custom_user",  # уникальное имя
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="custom_user_set",  # уникальное имя
        related_query_name="custom_user",
    )

    # ВАРИАНТ 1: избранные проекты
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
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
        # Генерирует аватар с первой буквой имени
        colors = [
            (73, 109, 137),
            (76, 114, 92),
            (156, 110, 86),
            (114, 86, 128),
            (179, 102, 79),
            (82, 119, 112),
        ]
        bg_color = random.choice(colors)

        img = Image.new("RGB", (200, 200), bg_color)
        draw = ImageDraw.Draw(img)

        letter = self.name[0].upper() if self.name else "?"
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2

        draw.text((x, y), letter, fill=(255, 255, 255), font=font)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name=f"avatar_{self.email}.png")
