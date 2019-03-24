from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
# from users.models import Team
# Create your models here.

class Tag(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z+]*$', '小英数字+だけね')
    name = models.CharField(_('タグ'), max_length=150, blank=True, validators=[alphanumeric])
    # vcolor = RegexValidator(r'^[0-9a-zA-Z]*$', '英数字だけね')
    # color = models.CharField(_('カラーコード'), max_length=6, blank=True, validators=[vcolor])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('タグ')
        verbose_name_plural = _('タグ')

class Category(models.Model):
    name = models.CharField(max_length=100)
    vcolor = RegexValidator(r'^[0-9a-zA-Z]*$', '英数字だけね')
    color = models.CharField(_('カラーコード'), max_length=6, blank=True, validators=[vcolor])
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = _('カテゴリー')
        verbose_name_plural = _('カテゴリー')


class Project(models.Model):
    # キャンプ
    name = models.CharField(_('タイトル'), max_length=100, blank=True)
    content = models.TextField(_('内容'), blank=True)
    # header = models.URLField(_('ヘッダー'), blank=True)
    header = models.ImageField(_('ヘッダー'),upload_to='header/', blank=True)
    place = models.CharField(_('開催場所'), max_length=100, blank=True)
    contact = models.CharField(_('連絡先'), max_length=100, blank=True)
    tags = models.ManyToManyField(
        Tag,
        verbose_name=_('tags'),
        blank=True,
        help_text=_('Specific tags for this user.'),
        related_name="projects",
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="host_projects", verbose_name=_('代表者'), on_delete=models.CASCADE, blank=True, null=True)

    is_public = models.BooleanField(
        _('public status'),
        default=True,
        help_text=_(
            '公開かどうか'),
    )    

    start_at = models.DateTimeField(default=timezone.now)
    end_at = models.DateTimeField(default=timezone.now)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # 使ってない
    team = models.ForeignKey('users.Team', related_name="host_projects", verbose_name=_('代表サークル'), on_delete=models.CASCADE, blank=True, null=True)
    url =  models.URLField(_('ホームページ url'), blank=True)
    logo = models.URLField(_('logo'), blank=True)
    category = models.ForeignKey('Category', related_name="projects", verbose_name=_('カテゴリー'), on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('キャンプ')
        verbose_name_plural = _('キャンプ')
