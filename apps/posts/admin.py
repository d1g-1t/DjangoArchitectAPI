"""
Административная панель для Posts.

Настройка отображения моделей в Django Admin.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Post, Category, Location


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки админки для Category."""
    
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Публикация', {
            'fields': ('is_published',)
        }),
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Настройки админки для Location."""
    
    list_display = ('name', 'is_published', 'posts_count', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    
    def posts_count(self, obj):
        """Количество постов в локации."""
        count = obj.posts.count()
        return format_html('<b>{}</b>', count)
    
    posts_count.short_description = 'Постов'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройки админки для Post."""
    
    list_display = (
        'title', 'author', 'category', 'location',
        'pub_date', 'is_published', 'status_badge'
    )
    list_filter = (
        'is_published', 'category', 'location',
        'pub_date', 'created_at'
    )
    search_fields = ('title', 'text', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'pub_date'
    raw_id_fields = ('author',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'text', 'image')
        }),
        ('Категоризация', {
            'fields': ('category', 'location')
        }),
        ('Публикация', {
            'fields': ('author', 'pub_date', 'is_published'),
            'description': 'Настройки публикации поста'
        }),
    )
    
    def status_badge(self, obj):
        """Визуальный индикатор статуса публикации."""
        if obj.is_published_now:
            return format_html(
                '<span style="color: green;">●</span> Опубликован'
            )
        elif obj.is_published:
            return format_html(
                '<span style="color: orange;">●</span> Запланирован'
            )
        else:
            return format_html(
                '<span style="color: red;">●</span> Черновик'
            )
    
    status_badge.short_description = 'Статус'
    
    def save_model(self, request, obj, form, change):
        """Автоматическое назначение автора при создании."""
        if not change:  # Если создается новый объект
            obj.author = request.user
        super().save_model(request, obj, form, change)
