# Generated by Django 3.1.5 on 2021-02-01 20:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_board', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='title',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='api_board.title'),
        ),
    ]