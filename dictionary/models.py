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
        help_text="Формат: АБВГ-ЦЦ-ЦЦ (например, АБВГ-12-34)"
    )
    vk_link = models.URLField(max_length=200, blank=True, null=True)
    telegram_link = models.URLField(max_length=200, blank=True, null=True)

    def clean(self):
        if self.group:
            pattern = r'^[А-ЯЁ]{4}-\d{2}-\d{2}$'
            if not re.match(pattern, self.group):
                raise ValidationError("Группа должна быть в формате АБВГ-ЦЦ-ЦЦ (например, АБВГ-12-34)")

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

class CardSet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_sets')
    tags = models.ManyToManyField('Tag', related_name='card_sets', blank=True)
    entries = models.ManyToManyField('DictionaryEntry', related_name='card_sets', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Набор карточек"
        verbose_name_plural = "Наборы карточек"

class FavoriteCardSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_card_sets')
    card_set = models.ForeignKey(CardSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'card_set')
        verbose_name = "Избранный набор карточек"
        verbose_name_plural = "Избранные наборы карточек"

    def __str__(self):
        return f"{self.user.username} - {self.card_set.name}"

class DictionaryEntry(models.Model):
    eng_term = models.CharField(max_length=100, unique=True)
    rus_term = models.CharField(max_length=100)
    transcription = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Описание на английском
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    audio = models.FileField(upload_to='audio/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.eng_term

    class Meta:
        verbose_name = "Словарная запись"
        verbose_name_plural = "Словарные записи"

class Phrase(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='phrases')
    eng_phrase = models.CharField(max_length=200)
    rus_phrase = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.eng_phrase} - {self.rus_phrase}"

    class Meta:
        verbose_name = "Фраза"
        verbose_name_plural = "Фразы"

class Example(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField()

    def __str__(self):
        return self.text[:50] + "..." if len(self.text) > 50 else self.text

    class Meta:
        verbose_name = "Пример"
        verbose_name_plural = "Примеры"

class Link(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

    def __str__(self):
        return self.url

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

class DictionaryTag(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('entry', 'tag')
        verbose_name = "Тег словарной записи"
        verbose_name_plural = "Теги словарных записей"

    def __str__(self):
        return f"{self.entry.eng_term} - {self.tag.name}"

class FavoriteEntry(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'entry')
        verbose_name = "Избранная запись"
        verbose_name_plural = "Избранные записи"

    def __str__(self):
        return f"{self.user.username} - {self.entry.eng_term}"

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Вы можете использовать HTML для форматирования текста")
    file = models.FileField(upload_to='articles/files/', null=True, blank=True, help_text="Загрузите файл (например, изображение или документ)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

class VocabularyTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary_topics')
    name = models.CharField(max_length=100)
    entries = models.ManyToManyField(DictionaryEntry, related_name='vocabulary_topics', blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = "Тема словарника"
        verbose_name_plural = "Темы словарника"

class FavoriteVocabularyTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_vocabulary_topics')
    topic = models.ForeignKey(VocabularyTopic, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'topic')
        verbose_name = "Избранная тема словарника"
        verbose_name_plural = "Избранные темы словарника"

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"