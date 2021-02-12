from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model
    """
    ROLE_CHOICES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin')
    )
    # TODO: поправить юзера
    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
    )
    bio = models.CharField(max_length=256, blank=True)
    role = models.CharField(max_length=10,
                            choices=ROLE_CHOICES,
                            default=ROLE_CHOICES[0],
                            help_text="Administrator, moderator or user. By default 'user'")

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('username',)

    def __str__(self):
        return self.username


class Comment(models.Model):
    """
    Comment model
    """
    text = models.CharField(max_length=655)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')
    review = models.ForeignKey('Review',
                               on_delete=models.CASCADE,
                               related_name='comments')
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Category(models.Model):
    """
    Category models
    """
    # TODO: Или убрать слаг или первичным ключом сделать
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Title(models.Model):
    """
    Title models
    """
    name = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    description = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='titles')
    genre = models.ManyToManyField('Genre', related_name='genres')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """
    Genre models
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Review models
    """
    text = models.TextField()
    score = models.SmallIntegerField(validators=[MaxValueValidator(10),
                                                 MinValueValidator(1)])
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'],
                                    name='unique_author_title'),
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return Truncator(self.text).chars(120)
