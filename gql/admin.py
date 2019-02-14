from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.safestring import mark_safe
# Register your models here.
from .models import Tag, Category, Project

# タグ
@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# キャンプ
@admin.register(Project)
class AdminProject(admin.ModelAdmin):
    list_display = ['name','is_public']
    search_fields = ['name','is_public','category__name','tags__name']
    fieldsets = (
        (None, {'fields': (('is_public','user','team'),'name', 'content')}),
        (_('URL info'), {'fields': ('header', 'logo','url')}),
        (_('Model info'), {'fields': ('category','tags')}),
        (_('Important dates'), {'fields': ('start_at', 'end_at','created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ['tags']

# Category
@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name','color','showcolor']
    search_fields = ['name','color']
    def showcolor(self, obj):
        return mark_safe('<b style="background:{}; color: white; padding: 5px;">{}</b>'.format('#'+obj.color, '#'+obj.color))