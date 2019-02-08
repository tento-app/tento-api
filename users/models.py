from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
import uuid as uuid_lib

from gql.models import Tag,Project

# Create your models here.

class University(models.Model):
    """大学"""

    name = models.CharField(_('大学'), max_length=150, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('大学')
        verbose_name_plural = _('大学')

class Department(models.Model):
    """学部"""

    name = models.CharField(_('学部'), max_length=150, blank=True)
    university = models.ForeignKey(
        University,
        verbose_name=_('大学'),
        blank=True,
        help_text=_('Specific University for this user.'),
        related_name="departments",
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('学部')
        verbose_name_plural = _('学部')

class Team(models.Model):
    """Team サークル"""

    name = models.CharField(_('Team'), max_length=150, blank=True)
    content = models.TextField(_('Team content'), blank=True)
    owner = models.ForeignKey('User', related_name="ownteams", verbose_name=_('代表者'), on_delete=models.CASCADE, blank=True, null=True)
    is_official = models.BooleanField(
        _('official status'),
        default=False,
        help_text=_(
            '公認サークルかどうか'),
    )
    header = models.URLField(_('header'), blank=True)
    logo = models.URLField(_('logo'), blank=True)
    url =  models.URLField(_('url'), blank=True)
    university = models.ForeignKey(
        University,
        verbose_name=_('大学'),
        blank=True,
        help_text=_('Specific University for this user.'),
        related_name="teams",
        on_delete=models.CASCADE,
        null=True
    )
    tags = models.ManyToManyField(
        'gql.Tag',
        verbose_name=_('tags'),
        blank=True,
        help_text=_('Specific tags for this user.'),
        related_name="teams",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('サークル')
        verbose_name_plural = _('サークル')

class Course(models.Model):
    """コース・学科"""

    name = models.CharField(_('コース・学科'), max_length=150, blank=True)
    department = models.ForeignKey(
        Department,
        verbose_name=_('学部'),
        blank=True,
        help_text=_('Specific Department for this user.'),
        related_name="courses",
        on_delete=models.CASCADE,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('コース・学科')
        verbose_name_plural = _('コース・学科')

class User(AbstractBaseUser, PermissionsMixin):
    """ユーザー AbstractUserをコピペし編集"""

    uuid = models.UUIDField(default=uuid_lib.uuid4,
                            primary_key=True, editable=False)
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    name = models.CharField(_('Display Name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    university = models.ForeignKey(
        University,
        verbose_name=_('大学'),
        blank=True,
        help_text=_('Specific University for this user.'),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True
    )
    department = models.ForeignKey(
        Department,
        verbose_name=_('学部'),
        blank=True,
        help_text=_('Specific Departments for this user.'),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True
    )
    teams = models.ManyToManyField(
        Team,
        verbose_name=_('サークル'),
        blank=True,
        help_text=_('Specific サークル for this user.'),
        related_name="users",
    )
    course = models.ForeignKey(
        Course,
        verbose_name=_('コース'),
        blank=True,
        help_text=_('Specific course for this user.'),
        related_name="users",
        on_delete=models.SET_NULL,
        null=True
    )
    tags = models.ManyToManyField(
        'gql.Tag',
        verbose_name=_('tags'),
        blank=True,
        help_text=_('Specific tags for this user.'),
        related_name="users",
    )
    projects = models.ManyToManyField(
        'gql.Project',
        verbose_name=_('キャンプ'),
        blank=True,
        help_text=_('Specific Project for this user.'),
        related_name="users",
    )

    content = models.TextField(_('User content'), blank=True)
    header = models.URLField(_('header'), blank=True)
    logo = models.URLField(_('logo'), blank=True)
    url =  models.URLField(_('url'), blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        verbose_name = _('ユーザー')
        verbose_name_plural = _('ユーザー')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    # 既存メソッドの変更
    def get_name(self):
        return self.name

    def get_short_name(self):
        return self.name