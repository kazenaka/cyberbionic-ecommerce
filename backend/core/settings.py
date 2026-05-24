from datetime import timedelta

# Указываем DRF использовать JWT авторизацию по умолчанию
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Подключаем фильтры глобально
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Настройки времени жизни токена
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), # Токен живет ровно 24 часа
    'AUTH_HEADER_TYPES': ('Bearer',), # Фронтенд будет слать заголовок: Authorization: Bearer <token>
}

# 1. Добавляем приложение в установленные
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Сторонние библиотеки
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'corsheaders', # <--- Наша библиотека CORS
    
    # Наши приложения
    'api',
]

# 2. ВАЖНО: Добавляем Middleware. 
# CorsMiddleware ОБЯЗАТЕЛЬНО должен стоять ВЫШЕ, чем CommonMiddleware!
# Это частый вопрос на собеседованиях. Если поставить ниже, Django заблокирует запрос до того, как сработает CORS.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # <--- Добавляем сюда!
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 3. Настройки доступа CORS (добавляем в конец файла)
# Для локальной разработки и проверки (MVP) мы можем разрешить запросы со всех доменов:
CORS_ALLOW_ALL_ORIGINS = True

# Примечание Principal Engineer'а: 
# Когда будем деплоить проект в интернет (на продакшен), мы заменим CORS_ALLOW_ALL_ORIGINS = True на:
# CORS_ALLOWED_ORIGINS = [
#     "https://твой-сайт-на-github-pages.github.io",
# ]