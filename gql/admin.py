from django.contrib import admin
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.safestring import mark_safe
# Register your models here.
from .models import Tag, Category, Project
import urllib
# タグ
@admin.register(Tag)
class AdminTag(admin.ModelAdmin):
    list_display = ['name','img']
    search_fields = ['name',]
    fields = ['name','logo','image_tag']
    readonly_fields = ['image_tag']
    def img(self, obj):
        if obj.logo:
            return mark_safe('<img src="https://media.tento.app/{}" width="50" height="50" />'.format(urllib.parse.quote(obj.logo.name)))
        else:
            return mark_safe('<p>画像がありません</p>')

    def image_tag(self, obj):
        if obj.logo:
            return mark_safe('<img src="https://media.tento.app/{}" width="100" height="100" />'.format(urllib.parse.quote(obj.logo.name)))
        else:
            return mark_safe('<p>画像がありません</p>')
    img.short_description = 'Image'
    img.allow_tags = True

# キャンプ
@admin.register(Project)
class AdminProject(admin.ModelAdmin):
    list_display = ['name','is_public','is_open']
    search_fields = ['name','is_public','category__name','tags__name']
    fieldsets = (
        (None, {'fields': (('is_public','is_open','user','team'),'name', 'header', 'thumbnail', 'place', 'contact', 'content')}),
        (_('Model info'), {'fields': ('start_at', 'tags')}),
        (_('Important dates'), {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ['tags']

# Category
# @admin.register(Category)
# class AdminCategory(admin.ModelAdmin):
#     list_display = ['name','color','showcolor']
#     search_fields = ['name','color']
#     def showcolor(self, obj):
#         return mark_safe('<b style="background:{}; color: white; padding: 5px;">{}</b>'.format('#'+obj.color, '#'+obj.color))