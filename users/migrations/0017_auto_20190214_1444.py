# Generated by Django 2.1.7 on 2019-02-14 05:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_user_projects'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='team',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
