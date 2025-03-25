# dictionary/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import DictionaryEntry, FavoriteEntry, Tag, DictionaryTag, UserProfile, CardSet, FavoriteCardSet, Article, VocabularyTopic, FavoriteVocabularyTopic
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
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
        }

class ExtendedUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['group', 'vk_link', 'telegram_link']
        labels = {
            'group': 'Group',
            'vk_link': 'VK Link',
            'telegram_link': 'Telegram Link',
        }

class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = ['name', 'tags']
        labels = {
            'name': 'Set Name',
            'tags': 'Tags',
        }
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
        }

class VocabularyTopicForm(forms.ModelForm):
    class Meta:
        model = VocabularyTopic
        fields = ['name']
        labels = {
            'name': 'Topic Name',
        }

class AddWordsToTopicForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="Search Words",
        widget=forms.TextInput(attrs={'placeholder': 'Enter search query...'})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Select Tags",
        widget=forms.CheckboxSelectMultiple
    )
    entries = forms.ModelMultipleChoiceField(
        queryset=DictionaryEntry.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Select Words to Add"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' not in kwargs or 'search_query' not in kwargs['initial']:
            self.fields['entries'].queryset = DictionaryEntry.objects.all()
        if 'initial' in kwargs and 'search_query' in kwargs['initial']:
            search_query = kwargs['initial']['search_query']
            tag_ids = kwargs['initial'].get('tags', [])
            entries = DictionaryEntry.objects.all()
            if search_query:
                entries = entries.filter(
                    Q(eng_term__icontains=search_query) | Q(rus_term__icontains=search_query)
                )
            if tag_ids:
                entries = entries.filter(dictionarytag__tag__in=tag_ids).distinct()
            self.fields['entries'].queryset = entries

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
    
    return render(request, 'home.html', {'entries': entries, 'favorite_ids': favorite_ids, 'tags': tags})  # Убрали "dictionary/"

def entry_detail(request, eng_term):
    entry = get_object_or_404(DictionaryEntry, eng_term=eng_term)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteEntry.objects.filter(user=request.user, entry=entry).exists()
    return render(request, 'entry_detail.html', {'entry': entry, 'is_favorite': is_favorite})  # Убрали "dictionary/"

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
    
    return render(request, 'search.html', {'entries': entries, 'query': query, 'favorite_ids': favorite_ids, 'tags': tags})  # Убрали "dictionary/"

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
            messages.success(request, 'Card set created successfully!')
            return redirect('flashcards')
    else:
        form = CardSetForm()

    if card_set_id:
        card_set = get_object_or_404(CardSet, id=card_set_id)
        entries_from_entries = card_set.entries.all()
        entries_from_tags = DictionaryEntry.objects.filter(dictionarytag__tag__in=card_set.tags.all())
        entries = (entries_from_entries | entries_from_tags).distinct()
        entries = list(entries)
        request.session['card_set_name'] = card_set.name
        return render(request, 'flashcards.html', {
            'entries': entries,
            'card_set': card_set,
            'card_sets': card_sets,
            'tags': tags,
            'form': form,
            'favorite_card_set_ids': favorite_card_set_ids,
            'favorite_ids': favorite_ids,
        })  # Убрали "dictionary/"
    else:
        request.session['card_set_name'] = None

    return render(request, 'flashcards.html', {
        'card_sets': card_sets,
        'tags': tags,
        'form': form,
        'favorite_card_set_ids': favorite_card_set_ids,
    })  # Убрали "dictionary/"

@login_required
def vocabulary(request):
    default_topic, created = VocabularyTopic.objects.get_or_create(
        user=request.user,
        name="All Words",
        defaults={'is_default': True}
    )

    favorite_entries = FavoriteEntry.objects.filter(user=request.user).select_related('entry')
    default_topic.entries.set([fe.entry for fe in favorite_entries])

    topics = VocabularyTopic.objects.filter(user=request.user).order_by('is_default', 'name')

    favorite_topic_ids = FavoriteVocabularyTopic.objects.filter(user=request.user).values_list('topic_id', flat=True)
    favorite_topic_ids = list(favorite_topic_ids)

    if request.method == 'POST' and 'create_topic' in request.POST:
        form = VocabularyTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.is_default = False
            topic.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('vocabulary')
    else:
        form = VocabularyTopicForm()

    return render(request, 'vocabulary.html', {
        'topics': topics,
        'form': form,
        'favorite_topic_ids': favorite_topic_ids,
    })  # Убрали "dictionary/"

@login_required
def add_words_to_topic(request, topic_id):
    topic = get_object_or_404(VocabularyTopic, id=topic_id, user=request.user)
    initial_data = {}
    if request.method == 'GET' and 'search_query' in request.GET:
        initial_data['search_query'] = request.GET['search_query']
    if request.method == 'GET' and 'tags' in request.GET:
        initial_data['tags'] = request.GET.getlist('tags')

    if request.method == 'POST':
        form = AddWordsToTopicForm(request.POST)
        if form.is_valid():
            topic.entries.add(*form.cleaned_data['entries'])
            messages.success(request, 'Words added to topic successfully!')
            return redirect('vocabulary')
    else:
        form = AddWordsToTopicForm(initial=initial_data)
    return render(request, 'add_words_to_topic.html', {
        'form': form,
        'topic': topic,
    })  # Убрали "dictionary/"

@login_required
def add_topic_to_favorites(request, topic_id):
    topic = get_object_or_404(VocabularyTopic, id=topic_id)
    FavoriteVocabularyTopic.objects.get_or_create(user=request.user, topic=topic)
    return redirect('vocabulary')

@login_required
def remove_topic_from_favorites(request, topic_id):
    topic = get_object_or_404(VocabularyTopic, id=topic_id)
    FavoriteVocabularyTopic.objects.filter(user=request.user, topic=topic).delete()
    return redirect('vocabulary')

@login_required
def personal_lists(request):
    entries = DictionaryEntry.objects.all()[:10]
    return render(request, 'personal_lists.html', {'entries': entries})  # Убрали "dictionary/"

def articles(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'articles.html', {'articles': articles})  # Убрали "dictionary/"

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Error during registration. Please check your input.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})  # Убрали "dictionary/"

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
    favorite_topics = FavoriteVocabularyTopic.objects.filter(user=request.user).select_related('topic')
    topics = [ft.topic for ft in favorite_topics]
    return render(request, 'favorites.html', {
        'entries': entries,
        'card_sets': card_sets,
        'topics': topics,
    })  # Убрали "dictionary/"

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
                messages.success(request, 'Password changed successfully!')
                return redirect('logout')
            else:
                messages.error(request, 'Error changing password. Please check your input.')
        else:
            user_form = UserProfileForm(request.POST, instance=request.user)
            profile_form = ExtendedUserProfileForm(request.POST, instance=profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating profile. Please check your input.')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ExtendedUserProfileForm(instance=profile)

    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
    })  # Убрали "dictionary/"

def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')