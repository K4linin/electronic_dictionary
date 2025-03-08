# dictionary/admin.py
from django.contrib import admin
from .models import DictionaryEntry, Phrase, Example, Link, Tag, DictionaryTag, FavoriteEntry, UserProfile, CardSet, FavoriteCardSet, Article

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

@admin.register(CardSet)
class CardSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    filter_horizontal = ('tags', 'entries')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'updated_at')

admin.site.register(Tag)
admin.site.register(FavoriteEntry)
admin.site.register(UserProfile)
admin.site.register(FavoriteCardSet)