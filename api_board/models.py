from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator


def validate_role(value):
    # TODO: Проверить правильность создания роли и работы валидатора и необходимость его
    role = ['user', 'admin', 'moderator']
    if value not in role and role is not None:
        raise ValidationError(f'Invalid data, choose from {role}')


class User(AbstractUser):
    """
    Custom user model
    """
    # TODO: поправить юзера
    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
    )
    bio = models.CharField(max_length=654, blank=True)
    role = models.CharField(max_length=20, default='user', validators=[validate_role])

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class Comment(models.Model):
    """
    Comment model
    """
    text = models.CharField(max_length=255)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    review = models.ForeignKey('Review',
                               on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        return self.text


class Category(models.Model):
    """
    Category models
    """
    # TODO: Или убрать слаг или первичным ключом сделать
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Title models
    """
    name = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='titles')
    genre = models.ManyToManyField('Genre', related_name='genres')

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Genre models
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Review models
    """
    text = models.TextField()
    score = models.SmallIntegerField(validators=[MaxValueValidator(10),
                                                 MinValueValidator(0)])
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews',
                              default=1)

    def __str__(self):
        return self.text
