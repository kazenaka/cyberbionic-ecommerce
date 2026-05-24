from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import (
    RegisterUserView, UserProfileView, CategoryViewSet, 
    ProductViewSet, CartView, CheckoutView, OrderHistoryView
)

# Используем DefaultRouter для автоматической генерации путей для ViewSets (Категории и Товары)
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    # 1. Каталог (подключаем сгенерированные роутером пути)
    path('', include(router.urls)), 
    
    # 2. Авторизация и профиль
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'), # Эндпоинт SimpleJWT для выдачи токена
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # 3. Корзина и заказы
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderHistoryView.as_view(), name='orders'),
]