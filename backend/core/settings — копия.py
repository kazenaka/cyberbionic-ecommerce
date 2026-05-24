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