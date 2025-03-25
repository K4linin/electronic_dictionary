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
        help_text="Format: АБВГ-ЦЦ-ЦЦ (e.g., АБВГ-12-34)"
    )
    vk_link = models.URLField(max_length=200, blank=True, null=True)
    telegram_link = models.URLField(max_length=200, blank=True, null=True)

    def clean(self):
        if self.group:
            pattern = r'^[А-ЯЁ]{4}-\d{2}-\d{2}$'
            if not re.match(pattern, self.group):
                raise ValidationError("Group must be in the format АБВГ-ЦЦ-ЦЦ (e.g., АБВГ-12-34)")

    def __str__(self):
        return f"Profile of {self.user.username}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class CardSet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_sets')
    tags = models.ManyToManyField('Tag', related_name='card_sets', blank=True)
    entries = models.ManyToManyField('DictionaryEntry', related_name='card_sets', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Card Set"
        verbose_name_plural = "Card Sets"

class FavoriteCardSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_card_sets')
    card_set = models.ForeignKey(CardSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'card_set')
        verbose_name = "Favorite Card Set"
        verbose_name_plural = "Favorite Card Sets"

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

    class Meta:
        verbose_name = "Dictionary Entry"
        verbose_name_plural = "Dictionary Entries"

class Phrase(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='phrases')
    eng_phrase = models.CharField(max_length=200)
    rus_phrase = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Phrase"
        verbose_name_plural = "Phrases"

class Example(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='examples')
    text = models.TextField()

    class Meta:
        verbose_name = "Example"
        verbose_name_plural = "Examples"

class Link(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE, related_name='links')
    url = models.URLField()

    class Meta:
        verbose_name = "Link"
        verbose_name_plural = "Links"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

class DictionaryTag(models.Model):
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Dictionary Tag"
        verbose_name_plural = "Dictionary Tags"

class FavoriteEntry(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    entry = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'entry')
        verbose_name = "Favorite Entry"
        verbose_name_plural = "Favorite Entries"

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="You can use HTML to format the text")
    file = models.FileField(upload_to='articles/files/', null=True, blank=True, help_text="Upload a file (e.g., image or document)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

class VocabularyTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary_topics')
    name = models.CharField(max_length=100)
    entries = models.ManyToManyField(DictionaryEntry, related_name='vocabulary_topics', blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = "Vocabulary Topic"
        verbose_name_plural = "Vocabulary Topics"

class FavoriteVocabularyTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_vocabulary_topics')
    topic = models.ForeignKey(VocabularyTopic, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'topic')
        verbose_name = "Favorite Vocabulary Topic"
        verbose_name_plural = "Favorite Vocabulary Topics"

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"