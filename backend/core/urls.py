from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),          # Наша мощная админка
    path('api/v1/', include('api.urls')),     # Все запросы к API отправляем в наше приложение (версионирование - это признак Senior-подхода)
]