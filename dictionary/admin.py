# dictionary/admin.py

from django.contrib import admin
from .models import DictionaryEntry, Phrase, Example, Link, Tag, DictionaryTag, FavoriteEntry, UserProfile, CardSet, FavoriteCardSet, Article, VocabularyTopic, FavoriteVocabularyTopic

class PhraseInline(admin.TabularInline):
    model = Phrase
    extra = 1

class ExampleInline(admin.TabularInline):
    model = Example
    extra = 1

class LinkInline(admin.TabularInline):
    model = Link
    extra = 1

class DictionaryTagInline(admin.TabularInline):
    model = DictionaryTag
    extra = 1

@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    inlines = [PhraseInline, ExampleInline, LinkInline, DictionaryTagInline]
    list_display = ('eng_term', 'rus_term', 'created_at')
    search_fields = ('eng_term', 'rus_term')
    list_display_links = ('eng_term', 'rus_term')
    list_filter = ('created_at',)
    ordering = ('eng_term',)

@admin.register(CardSet)
class CardSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    list_filter = ('user',)
    filter_horizontal = ('tags', 'entries')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'updated_at')

@admin.register(VocabularyTopic)
class VocabularyTopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_default')
    list_filter = ('user', 'is_default')
    filter_horizontal = ('entries',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FavoriteEntry)
class FavoriteEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry')
    list_filter = ('user',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')
    list_filter = ('group',)

@admin.register(FavoriteCardSet)
class FavoriteCardSetAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_set')
    list_filter = ('user',)

@admin.register(FavoriteVocabularyTopic)
class FavoriteVocabularyTopicAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic')
    list_filter = ('user',)