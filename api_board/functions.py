from random import randint

from django.utils.text import slugify


def generate_username(obj, email):
    """Return unique username.

    :param obj: object of default User model
    :type obj: User model
    :param email: Email,which the user specified during registration
    :type email:str
    :rtype: str
    :return: Unique username.
    """
    username = email.split('@')[0]
    while obj.objects.filter(username=username).exists():
        username += str(randint(0, 9))
    return username


def generate_slug(slug, name, obj):
    """Generate unique slug from name if slug param doesnt exist, return slug.

    :param slug: None or str slug
    :param name: Name of category of genre
    :param obj: Category or genre object

    :return: Unique slug
    """
    if slug is None:
        slug = slugify(name)
    else:
        slug = slugify(slug)
    while obj.objects.filter(slug=slug):
        slug += str(randint(0, 10))
    return slug
