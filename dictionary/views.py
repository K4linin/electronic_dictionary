# dictionary/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import DictionaryEntry, FavoriteEntry, Tag, DictionaryTag, UserProfile, CardSet, FavoriteCardSet, Article
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ExtendedUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['group', 'vk_link', 'telegram_link']
        labels = {
            'group': 'Группа',
            'vk_link': 'ВКонтакте',
            'telegram_link': 'Telegram',
        }

class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['name', 'tags']
        labels = {
            'name': 'Название набора',
            'tags': 'Теги',
        }
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

def home(request):
    tag_id = request.GET.get('tag')
    entries = DictionaryEntry.objects.all()
    
    if tag_id:
        entries = entries.filter(dictionarytag__tag__id=tag_id)
    
    tags = Tag.objects.all()

    if request.user.is_authenticated:
        favorite_ids = FavoriteEntry.objects.filter(user=request.user).values_list('entry_id', flat=True)
    else:
        favorite_ids = []
    
    return render(request, 'dictionary/home.html', {'entries': entries, 'favorite_ids': favorite_ids, 'tags': tags})

def entry_detail(request, eng_term):
    entry = get_object_or_404(DictionaryEntry, eng_term=eng_term)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteEntry.objects.filter(user=request.user, entry=entry).exists()
    return render(request, 'dictionary/entry_detail.html', {'entry': entry, 'is_favorite': is_favorite})

def search(request):
    query = request.GET.get('q', '')
    tag_id = request.GET.get('tag')
    entries = DictionaryEntry.objects.all()
    
    if query:
        tag = Tag.objects.filter(name__iexact=query).first()
        if tag:
            entries = entries.filter(dictionarytag__tag=tag)
        else:
            entries = entries.filter(
                Q(eng_term__icontains=query) | Q(rus_term__icontains=query)
            )
    
    if tag_id:
        entries = entries.filter(dictionarytag__tag__id=tag_id)
    
    tags = Tag.objects.all()

    if request.user.is_authenticated:
        favorite_ids = FavoriteEntry.objects.filter(user=request.user).values_list('entry_id', flat=True)
    else:
        favorite_ids = []
    
    return render(request, 'dictionary/search.html', {'entries': entries, 'query': query, 'favorite_ids': favorite_ids, 'tags': tags})

@login_required
def flashcards(request):
    card_set_id = request.GET.get('card_set')
    tag_id = request.GET.get('tag')
    tags = Tag.objects.all()

    card_sets = CardSet.objects.all()
    if tag_id:
        card_sets = card_sets.filter(tags__id=tag_id)

    if request.user.is_authenticated:
        favorite_card_set_ids = FavoriteCardSet.objects.filter(user=request.user).values_list('card_set_id', flat=True)
        favorite_ids = FavoriteEntry.objects.filter(user=request.user).values_list('entry_id', flat=True)
        # Преобразуем QuerySet в список
        favorite_card_set_ids = list(favorite_card_set_ids)
        favorite_ids = list(favorite_ids)
    else:
        favorite_card_set_ids = []
        favorite_ids = []

    if request.method == 'POST' and 'create_set' in request.POST:
        form = CardSetForm(request.POST)
        if form.is_valid():
            card_set = form.save(commit=False)
            card_set.user = request.user
            card_set.save()
            form.save_m2m()
            messages.success(request, 'Набор карточек создан!')
            return redirect('flashcards')
    else:
        form = CardSetForm()

    if card_set_id:
        card_set = get_object_or_404(CardSet, id=card_set_id)
        # Получаем слова из поля entries
        entries_from_entries = card_set.entries.all()
        # Получаем слова из тегов
        entries_from_tags = DictionaryEntry.objects.filter(dictionarytag__tag__in=card_set.tags.all())
        # Объединяем и убираем дубликаты
        entries = (entries_from_entries | entries_from_tags).distinct()
        # Принудительно материализуем Queryset в список
        entries = list(entries)
        request.session['card_set_name'] = card_set.name
        # Отладка
        print("Entries from entries:", entries_from_entries.count())
        print("Entries from tags:", entries_from_tags.count())
        print("Total entries:", len(entries))
        print("Entries list:", entries)
        for entry in entries:
            print("Entry:", entry.eng_term, entry.rus_term, entry.transcription)
        return render(request, 'dictionary/flashcards.html', {
            'entries': entries,
            'card_set': card_set,
            'card_sets': card_sets,
            'tags': tags,
            'form': form,
            'favorite_card_set_ids': favorite_card_set_ids,
            'favorite_ids': favorite_ids,
        })
    else:
        request.session['card_set_name'] = None

    return render(request, 'dictionary/flashcards.html', {
        'card_sets': card_sets,
        'tags': tags,
        'form': form,
        'favorite_card_set_ids': favorite_card_set_ids,
    })

@login_required
def vocabulary(request):
    entries = DictionaryEntry.objects.all()[:10]
    return render(request, 'dictionary/vocabulary.html', {'entries': entries})

@login_required
def personal_lists(request):
    entries = DictionaryEntry.objects.all()[:10]
    return render(request, 'dictionary/personal_lists.html', {'entries': entries})

def articles(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'dictionary/articles.html', {'articles': articles})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка при регистрации. Проверьте введённые данные.')
    else:
        form = UserCreationForm()
    return render(request, 'dictionary/register.html', {'form': form})

@login_required
def add_to_favorites(request, eng_term):
    entry = get_object_or_404(DictionaryEntry, eng_term=eng_term)
    FavoriteEntry.objects.get_or_create(user=request.user, entry=entry)
    next_url = request.GET.get('next', 'home')
    if next_url == 'home':
        return redirect('home')
    elif next_url == 'search':
        query = request.GET.get('q', '')
        tag = request.GET.get('tag', '')
        return redirect(f'/search/?q={query}&tag={tag}')
    else:
        return redirect('entry_detail', eng_term=eng_term)

@login_required
def remove_from_favorites(request, eng_term):
    entry = get_object_or_404(DictionaryEntry, eng_term=eng_term)
    FavoriteEntry.objects.filter(user=request.user, entry=entry).delete()
    next_url = request.GET.get('next', 'home')
    if next_url == 'home':
        return redirect('home')
    elif next_url == 'search':
        query = request.GET.get('q', '')
        tag = request.GET.get('tag', '')
        return redirect(f'/search/?q={query}&tag={tag}')
    else:
        return redirect('entry_detail', eng_term=eng_term)

@login_required
def add_cardset_to_favorites(request, card_set_id):
    card_set = get_object_or_404(CardSet, id=card_set_id)
    FavoriteCardSet.objects.get_or_create(user=request.user, card_set=card_set)
    return redirect('flashcards')

@login_required
def remove_cardset_from_favorites(request, card_set_id):
    card_set = get_object_or_404(CardSet, id=card_set_id)
    FavoriteCardSet.objects.filter(user=request.user, card_set=card_set).delete()
    return redirect('flashcards')

@login_required
def favorites(request):
    favorite_entries = FavoriteEntry.objects.filter(user=request.user).select_related('entry')
    entries = [fe.entry for fe in favorite_entries]
    favorite_card_sets = FavoriteCardSet.objects.filter(user=request.user).select_related('card_set')
    card_sets = [fcs.card_set for fcs in favorite_card_sets]
    return render(request, 'dictionary/favorites.html', {'entries': entries, 'card_sets': card_sets})

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Пароль успешно изменён!')
                return redirect('logout')
            else:
                messages.error(request, 'Ошибка при смене пароля. Проверьте введённые данные.')
        else:
            user_form = UserProfileForm(request.POST, instance=request.user)
            profile_form = ExtendedUserProfileForm(request.POST, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлён!')
                return redirect('profile')
            else:
                messages.error(request, 'Ошибка при обновлении профиля. Проверьте введённые данные.')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ExtendedUserProfileForm(instance=profile)

    return render(request, 'dictionary/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')