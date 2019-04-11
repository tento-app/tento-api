# Generated by Django 2.1.7 on 2019-04-11 12:09

import django.core.validators
from django.db import migrations, models
import django.utils.timezone
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('gql', '0038_auto_20190330_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='color',
            field=models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z]*$', '英数字だけね')], verbose_name='カラーコード'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(default='タイトル未記入', max_length=100, verbose_name='タイトル'),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='thumbnail',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format=None, keep_meta=True, null=True, quality=0, size=[500, 300], upload_to='thumbnail/', verbose_name='ヘッダーthumbnail'),
        ),
    ]