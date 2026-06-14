import re

from django.core.exceptions import ValidationError

from core.constants import GITHUB_DOMAIN, PHONE_REGEX


def validate_github_url(value):
    """Проверяет, что ссылка ведет на GitHub"""
    if value and GITHUB_DOMAIN not in value:
        raise ValidationError("Ссылка должна вести на GitHub.")


def validate_phone_format(value):
    """Проверяет формат телефонного номера"""
    if value and not re.match(PHONE_REGEX, value):
        raise ValidationError(
            "Номер должен быть в формате +7XXXXXXXXXX (10 цифр после +7)"
        )
