from .models import User, Department,Team,Course,University
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django import forms
from django.utils.translation import gettext, gettext_lazy as _

# Register your models here.

# 大学
@admin.register(University)
class AdminUniversity(admin.ModelAdmin):
    search_fields = ('id', 'name')

# 学部
@admin.register(Department)
class AdminDepartment(admin.ModelAdmin):
    list_display = ('name', 'university')
    search_fields = ('name','university__name')

# 学科・コース
@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('name','university','department')
    search_fields = ('name','university__name','department__name')
    def university(self,obj):
        return obj.department.university
    university.short_description = '大学'
    university.admin_order_field = 'departments__university'

# サークル
@admin.register(Team)
class AdminTeam(admin.ModelAdmin):
    list_display = ('name','university','is_official')
    search_fields = ('name','university__name','is_official')

# ユーザー
class AdminUserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(AdminUserAdminForm, self).__init__(*args, **kwargs)
        if self.instance.university:
            self.fields['department'].queryset = Department.objects.filter(university=self.instance.university)
        if self.instance.department:
            self.fields['course'].queryset = Course.objects.filter(department=self.instance.department)

@admin.register(User)
class AdminUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('URL info'), {'fields': ('header', 'logo','url')}),
        (_('Personal info'), {'fields': ('name', 'email','university','department','course','teams','projects','tags')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email','course', 'name', 'is_staff')
    search_fields = ('username', 'name', 'email','course__name','university__name','department__name')
    filter_horizontal = ('groups', 'user_permissions','teams','projects','tags')
    form = AdminUserAdminForm