"""
Модели для приложения Posts.

Архитектура:
- Category: Категории для постов
- Location: Географические локации
- Post: Основная модель публикаций

Best practices:
- Custom managers для оптимизированных запросов
- Database indexes для производительности
- Автоматическая генерация slug
- Soft delete pattern
- Timestamped models
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MaxLengthValidator


# ---------------------------------------------------------------------------
# Hard limits for text fields
# ---------------------------------------------------------------------------
# Maximum characters stored in Post.text.  Prevents unbounded storage and
# ensures that template filters (linebreaksbr, truncatewords, etc.) never
# have to iterate over megabytes of user-supplied content – a core cause of
# the Uncontrolled Resource Consumption CVEs (CVE-2024-38875, -41989, -41990,
# -41991, -45230).
MAX_POST_TEXT_LENGTH: int = 50_000  # ~12 500 words – generous for a blog post

# Characters shown in listing previews before the user clicks "read more".
MAX_PREVIEW_CHARS: int = 500


class TimestampedModel(models.Model):
    """
    Абстрактная модель с метками времени.
    
    Автоматически отслеживает время создания и обновления.
    """
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )
    
    class Meta:
        abstract = True


class PublishedManager(models.Manager):
    """
    Менеджер для получения опубликованных объектов.
    
    Оптимизирует запросы с помощью select_related и prefetch_related.
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
    
    def with_related(self):
        """Запрос со связанными объектами для оптимизации."""
        return self.get_queryset().select_related(
            'category', 'location'
        ).order_by('-pub_date')


class Category(TimestampedModel):
    """
    Модель категории постов.
    
    Примеры: Путешествия, Технологии, Личное и т.д.
    """
    title = models.CharField(
        'Название',
        max_length=256,
        unique=True
    )
    description = models.TextField(
        'Описание',
        blank=True,
        help_text='Краткое описание категории'
    )
    slug = models.SlugField(
        'Slug',
        max_length=64,
        unique=True,
        help_text='Уникальный идентификатор для URL'
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть категорию'
    )
    
    objects = models.Manager()
    published = PublishedManager()
    
    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']
        indexes = [
            models.Index(fields=['slug', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматическая генерация slug при создании."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('posts:category_posts', kwargs={'slug': self.slug})


class Location(TimestampedModel):
    """
    Модель географической локации.
    
    Описывает место написания или события в посте.
    """
    name = models.CharField(
        'Название места',
        max_length=256,
        unique=True
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True
    )
    
    objects = models.Manager()
    published = PublishedManager()
    
    class Meta:
        verbose_name = 'локация'
        verbose_name_plural = 'Локации'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_published']),
        ]
    
    def __str__(self):
        return self.name


class Post(TimestampedModel):
    """
    Модель публикации в блоге.
    
    Основная модель для хранения постов с поддержкой:
    - Отложенной публикации
    - Категоризации
    - Привязки к локации
    - Soft delete через is_published
    """
    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField(
        'Текст',
        help_text='Основное содержание поста',
        validators=[
            MaxLengthValidator(
                MAX_POST_TEXT_LENGTH,
                message=f'Текст публикации не может превышать {MAX_POST_TEXT_LENGTH:,} символов.'
            )
        ]
    )
    slug = models.SlugField(
        'Slug',
        max_length=256,
        unique=True,
        help_text='Уникальный идентификатор для URL'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить будущее время, пост будет опубликован в указанный момент',
        db_index=True
    )
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/images/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Основное изображение поста'
    )
    
    objects = models.Manager()
    published = PublishedManager()
    
    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date', '-created_at']
        indexes = [
            models.Index(fields=['-pub_date', 'is_published']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-pub_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматическая генерация slug при создании."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published_now(self) -> bool:
        """Проверка, опубликован ли пост на текущий момент."""
        return (
            self.is_published and
            self.pub_date <= timezone.now()
        )

    @property
    def preview_text(self) -> str:
        """
        Возвращает безопасно усечённый фрагмент текста для отображения
        в списках (индекс, категория).

        Ограничение в MAX_PREVIEW_CHARS символов гарантирует, что шаблонные
        фильтры, применяемые к этому значению, никогда не обрабатывают
        произвольно большой ввод — защита от Uncontrolled Resource Consumption.
        """
        raw = self.text or ''
        if len(raw) <= MAX_PREVIEW_CHARS:
            return raw
        # Truncate at word boundary to avoid cutting mid-word
        truncated = raw[:MAX_PREVIEW_CHARS]
        last_space = truncated.rfind(' ')
        if last_space > MAX_PREVIEW_CHARS // 2:
            truncated = truncated[:last_space]
        return truncated + '…'

    @property
    def safe_text(self) -> str:
        """
        Возвращает текст публикации, усечённый до MAX_POST_TEXT_LENGTH символов.

        Используется на странице детального просмотра вместо прямой передачи
        Post.text в шаблонные фильтры.  Даже если в БД оказалось значение
        длиннее лимита (например, записанное напрямую, минуя форму), шаблон
        никогда не получит неограниченный объём данных.
        """
        raw = self.text or ''
        return raw[:MAX_POST_TEXT_LENGTH]
