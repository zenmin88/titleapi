from random import randint

from django.utils.text import slugify


def generate_username(obj, email):
    """
    Generate unique username from email
    """
    username = email.split('@')[0]
    while obj.objects.filter(username=username).exists():
        username += str(randint(0, 9))
    return username


def generate_slug(slug, name, obj):
    """
    Generate unique slug from name
    """

    if slug is None:
        slug = slugify(name)
    else:
        slug = slugify(slug)
    while obj.objects.filter(slug=slug):
        slug += str(randint(0, 10))
    return slug
