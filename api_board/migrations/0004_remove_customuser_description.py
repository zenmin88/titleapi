# Generated by Django 3.1.5 on 2021-01-31 23:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_board', '0003_auto_20210131_0313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='description',
        ),
    ]
