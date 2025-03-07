# electronic_dictionary/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from dictionary import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dictionary.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='dictionary/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),  # Используем кастомное представление
    path('register/', views.register, name='register'),
    path('', include('social_django.urls', namespace='social')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)