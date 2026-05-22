"""
Конфигурация URL для проекта mysite.

Этот файл связывает адреса в строке браузера с логикой (views), которая должна работать.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Импортируем встроенные обработчики Django для Входа (Login) и Выхода (Logout)
from django.contrib.auth import views as auth_views
# Импортируем функции (views) из нашего приложения main для регистрации
from main import views as main_views

# Единый список всех маршрутов сайта (накапливаем всё в одном месте)
urlpatterns = [
    #Панель администратора
    path('admin/', admin.site.urls),
    
    #Подключение всех адресов приложения main (главная, карточка товара и т.д.)
    path('', include('main.urls')),
    
    #Страница регистрации пользователя: http://127.0.0.1:8000/register/
    path('register/', main_views.register, name='register'),
    
    #Страница входа в аккаунт: http://127.0.0.1:8000/login/
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    
    #Скрипт для выхода из аккаунта: http://127.0.0.1:8000/logout/
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    
    # Вот эта строчка свяжет ошибку 404 с нашей новой функцией профиля!
    path('accounts/profile/', main_views.profile, name='profile'), 
    
    path('register/', main_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]


# Важный блок: если включен режим разработки (DEBUG = True), 
# мы ДОБАВЛЯЕМ к общему списку маршрутов правила для обработки картинок (медиа-файлов)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)