# Generated by Django 2.1.7 on 2019-03-24 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gql', '0027_auto_20190324_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='header',
            field=models.ImageField(blank=True, upload_to='header/', verbose_name='ヘッダー'),
        ),
    ]
