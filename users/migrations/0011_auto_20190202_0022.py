# Generated by Django 2.1.5 on 2019-02-01 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20190202_0017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='university',
        ),
        migrations.RemoveField(
            model_name='team',
            name='department',
        ),
    ]
