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


def generate_slug(data, obj):
    """
    Generate unique slug
    # TODO: Переписать ужасно
    """
    if data.get('slug', None) is None:
        data['slug'] = slugify(data['name'])
    else:
        data['slug'] = slugify(data['slug'])
    while obj.objects.filter(slug=data['slug']):
        data['slug'] += str(randint(0, 10))
    return data['slug']
