# Generated by Django 3.1.6 on 2021-02-05 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_board', '0004_auto_20210205_0606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(),
        ),
    ]
