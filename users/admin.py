from .models import User, Department,Team,Course,University
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
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
    search_fields = ('name','university')

# 学科・コース
@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ('name','university','department')
    search_fields = ('name','university','department')
    def university(self,obj):
        return obj.department.university
    university.short_description = '大学'
    university.admin_order_field = 'departments__university'

# サークル
@admin.register(Team)
class AdminTeam(admin.ModelAdmin):
    list_display = ('name','university','is_official')
    search_fields = ('name','university','is_official')

@admin.register(User)
class AdminUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('name', 'email','university','department','course','teams','projects','tags')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'email','course', 'name', 'is_staff')
    search_fields = ('username', 'name', 'email')
    filter_horizontal = ('groups', 'user_permissions','teams','projects','tags')