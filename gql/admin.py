from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _

# Register your models here.
from gql.models import Tag, Category, Project

# タグ
@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# キャンプ
@admin.register(Project)
class AdminProject(admin.ModelAdmin):
    list_display = ['name','is_public']
    search_fields = ['name','is_public']
    fieldsets = (
        (None, {'fields': (('is_public','user','team'),'name', 'content')}),
        (_('URL info'), {'fields': ('header', 'logo','url')}),
        (_('Model info'), {'fields': ('tags',)}),
        (_('Important dates'), {'fields': ('created_at', 'updated_at')}),
    )
    filter_horizontal = [ 'tags']

# Category
@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']