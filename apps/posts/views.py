"""
Views для приложения Posts.

Используются Class-Based Views для лучшей архитектуры.
Применяются оптимизации запросов и кэширование.
"""

from django.views.generic import ListView, DetailView
from django.core.cache import cache
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Post, Category


class PostListView(ListView):
    """
    Главная страница с лентой постов.
    
    Features:
    - Пагинация
    - Оптимизация запросов через select_related
    - Кэширование
    """
    model = Post
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE
    
    def get_queryset(self):
        """Получение опубликованных постов с оптимизацией."""
        cache_key = f'posts_list_page_{self.request.GET.get("page", 1)}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = Post.published.with_related()
            cache.set(cache_key, queryset, 300)  # 5 минут
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'DjangoArchitectAPI - Главная'
        return context


class PostDetailView(DetailView):
    """
    Детальная страница поста.
    
    Features:
    - Получение по slug
    - Оптимизация запросов
    - Кэширование
    """
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Оптимизированный запрос с related объектами."""
        return Post.published.with_related()
    
    def get_object(self, queryset=None):
        """Получение объекта с кэшированием."""
        slug = self.kwargs.get(self.slug_url_kwarg)
        cache_key = f'post_detail_{slug}'
        obj = cache.get(cache_key)
        
        if obj is None:
            obj = super().get_object(queryset)
            cache.set(cache_key, obj, 600)  # 10 минут
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        return context


class CategoryPostsView(ListView):
    """
    Страница постов определенной категории.
    
    Features:
    - Фильтрация по категории
    - Пагинация
    - Оптимизация запросов
    """
    model = Post
    template_name = 'posts/category.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE
    
    def get_queryset(self):
        """Посты отфильтрованные по категории."""
        self.category = get_object_or_404(
            Category.published,
            slug=self.kwargs['slug']
        )
        
        cache_key = f'category_posts_{self.category.slug}_page_{self.request.GET.get("page", 1)}'
        queryset = cache.get(cache_key)
        
        if queryset is None:
            queryset = Post.published.with_related().filter(
                category=self.category
            )
            cache.set(cache_key, queryset, 300)  # 5 минут
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['title'] = f'Категория: {self.category.title}'
        return context
