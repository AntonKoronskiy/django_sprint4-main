from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()


class Location (models.Model):
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Название места')

    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text="Снимите галочку, чтобы скрыть публикацию.")

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Заголовок')

    description = models.TextField(
        blank=True,
        verbose_name='Описание')

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name='Идентификатор',
        help_text=("Идентификатор страницы для URL;"
                   " разрешены символы латиницы, цифры,"
                   " дефис и подчёркивание.")
    )

    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text="Снимите галочку, чтобы скрыть публикацию.")

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Заголовок')

    text = models.TextField(
        blank=True,
        verbose_name='Текст')

    pub_date = models.DateTimeField(
        blank=True,
        verbose_name='Дата и время публикации',
        help_text=("Если установить дату и время в будущем"
                   " — можно делать отложенные публикации."))

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        null=True,
        on_delete=models.SET_NULL,
        blank=False,
        verbose_name='Местоположение',
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        blank=False,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True,
        upload_to='images')

    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text="Снимите галочку, чтобы скрыть публикацию.")

    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Автор',
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Пост',
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий',
        verbose_name_plural = 'Комментарии',
        ordering = ('created_at'),

    def __str__(self):
        return self.text[:20]
