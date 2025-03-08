# dictionary/models.py
from django.db import models
from django.contrib.auth.models import User
import re
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    group = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text="Формат: АААА-ЦЦ-ЦЦЦ() (например, АААА-12-345())"
    )
    vk_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="ВКонтакте")
    telegram_link = models.URLField(max_length=200, blank=True, null=True, verbose_name="Telegram")

    def clean(self):
        if self.group:
            pattern = r'^[А-ЯЁ]{4}-\d{2}-\d{3}\(\)$'
            if not re.match(pattern, self.group):
                raise ValidationError("Группа должна быть в формате АААА-ЦЦ-ЦЦЦ() (например, АААА-12-345())")

    def __str__(self):
        return f"Profile of {self.user.username}"

class CardSet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_sets')
    tags = models.ManyToManyField('Tag', related_name='card_sets', blank=True)
    entries = models.ManyToManyField('DictionaryEntry', related_name='card_sets', blank=True)

    def __str__(self):
        return self.name

class FavoriteCardSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_card_sets')
    card_set = models.ForeignKey(CardSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'card_set')

    def __str__(self):
        return f"{self.user.username} - {self.card_set.name}"

class DictionaryEntry(models.Model):
    eng_term = models.CharField(max_length=100, unique=True)
    eng_desc = models.TextField()
    transcription = models.CharField(max_length=50)
    rus_term = models.CharField(max_length=100)
    rus_desc = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    audio = models.FileField(upload_to='audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.eng_term

class Phrase(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='phrases')
    eng_phrase = models.CharField(max_length=200)
    rus_phrase = models.CharField(max_length=200)

class Example(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField()

class Link(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class DictionaryTag(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class FavoriteEntry(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'entry')

# Новая модель для статей
class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание", help_text="Можно использовать HTML для форматирования текста")
    file = models.FileField(upload_to='articles/files/', null=True, blank=True, verbose_name="Файл", help_text="Загрузите файл (например, изображение или документ)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"