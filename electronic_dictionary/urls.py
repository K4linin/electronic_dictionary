# electronic_dictionary/urls.py

from django.contrib import admin
from django.urls import path, include
from dictionary import views

admin.site.site_header = "Электронный словарь - Админ-панель"
admin.site.site_title = "Электронный словарь"
admin.site.index_title = "Добро пожаловать в админ-панель"

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('learning/flashcards/', views.flashcards, name='flashcards'),
    path('learning/vocabulary/', views.vocabulary, name='vocabulary'),
    path('learning/vocabulary/add-words/<int:topic_id>/', views.add_words_to_topic, name='add_words_to_topic'),
    path('learning/personal_lists/', views.personal_lists, name='personal_lists'),
    path('entry/<str:eng_term>/', views.entry_detail, name='entry_detail'),
    path('search/', views.search, name='search'),
    path('articles/', views.articles, name='articles'),
    path('favorites/', views.favorites, name='favorites'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('entry/<str:eng_term>/add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('entry/<str:eng_term>/remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('cardset/<int:card_set_id>/add-to-favorites/', views.add_cardset_to_favorites, name='add_cardset_to_favorites'),
    path('cardset/<int:card_set_id>/remove-from-favorites/', views.remove_cardset_from_favorites, name='remove_cardset_from_favorites'),
    path('topic/<int:topic_id>/add-to-favorites/', views.add_topic_to_favorites, name='add_topic_to_favorites'),
    path('topic/<int:topic_id>/remove-from-favorites/', views.remove_topic_from_favorites, name='remove_topic_from_favorites'),

]