from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError


# def validate_role(value):
#     # TODO: Проверить правильность создания роли и работы валидатора и необходимость его
#     role = ('user', 'admin', 'moderator')
#     if value not in role and role is not None:
#         raise ValidationError(f'Invalid data, role can be in {role}')


class CustomUser(AbstractUser):

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    description = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=20, default='user')





