# dictionary/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('entry/<str:eng_term>/', views.entry_detail, name='entry_detail'),
    path('search/', views.search, name='search'),
    path('favorites/', views.favorites, name='favorites'),
    path('profile/', views.profile, name='profile'),
    path('learning/flashcards/', views.flashcards, name='flashcards'),
    path('learning/vocabulary/', views.vocabulary, name='vocabulary'),
    path('learning/personal-lists/', views.personal_lists, name='personal_lists'),
    path('learning/articles/', views.articles, name='articles'),
    path('entry/<str:eng_term>/add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('entry/<str:eng_term>/remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('cardset/<int:card_set_id>/add-to-favorites/', views.add_cardset_to_favorites, name='add_cardset_to_favorites'),
    path('cardset/<int:card_set_id>/remove-from-favorites/', views.remove_cardset_from_favorites, name='remove_cardset_from_favorites'),
]