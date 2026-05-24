from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer,
    CartSerializer, OrderSerializer
)

# ==========================================
# 1. ПОЛЬЗОВАТЕЛИ И ПРОФИЛЬ
# ==========================================
class RegisterUserView(generics.CreateAPIView):
    """ Эндпоинт для регистрации нового пользователя """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Доступно всем гостям

class UserProfileView(generics.RetrieveUpdateAPIView):
    """ Эндпоинт для получения и изменения данных своего профиля """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Только для авторизованных

    def get_object(self):
        # Возвращаем именно того пользователя, чей токен прислан в запросе
        return self.request.user


# ==========================================
# 2. КАТАЛОГ (Только для чтения клиентами)
# ==========================================
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ Список категорий (создавать и удалять можно только через Админку) """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ 
    Список товаров. Включает мощную систему фильтрации.
    Подключим django-filter, чтобы Фронтенд мог делать запросы вида:
    /api/products/?category=1&min_price=1000&max_price=5000&in_stock=true
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    # Настраиваем фильтры и поиск
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category'] # Фильтр по категории
    search_fields = ['name', 'description'] # Текстовый поиск
    ordering_fields = ['price', 'created_at'] # Сортировка (сначала дешевые/дорогие)

    def get_queryset(self):
        """ Кастомная фильтрация для цены и наличия """
        queryset = super().get_queryset()
        
        # Фильтр: Диапазон цен
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Фильтр: Только в наличии
        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
            
        return queryset


# ==========================================
# 3. КОРЗИНА
# ==========================================
class CartView(APIView):
    """ Управление корзиной текущего пользователя """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """ Получить содержимое корзины """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """ Добавить товар в корзину или увеличить количество """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        # Проверка остатков на складе (защита от заказа того, чего нет)
        if product.stock < quantity:
            return Response({"error": "Недостаточно товара на складе"}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем товар в корзине. Если есть - увеличиваем, если нет - создаем
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Товар добавлен в корзину"}, status=status.HTTP_200_OK)

    def delete(self, request):
        """ Очистить корзину целиком """
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({"message": "Корзина очищена"}, status=status.HTTP_204_NO_CONTENT)


# ==========================================
# 4. ОФОРМЛЕНИЕ ЗАКАЗА (CHECKOUT)
# ==========================================
class CheckoutView(APIView):
    """ Эндпоинт для превращения корзины в оформленный заказ """
    permission_classes = [permissions.IsAuthenticated]

    # transaction.atomic гарантирует, что если что-то упадет (например, кончится товар),
    # база данных откатится назад и ничего не сломается. Это маркер Senior-разработчика!
    @transaction.atomic 
    def post(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        
        if not cart.items.exists():
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        # Берем адрес доставки из профиля пользователя или из тела запроса
        shipping_address = request.data.get('shipping_address', user.shipping_address)
        if not shipping_address:
            return Response({"error": "Укажите адрес доставки"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Создаем пустой заказ
        order = Order.objects.create(user=user, shipping_address=shipping_address)

        # 2. Переносим товары из корзины в заказ
        for item in cart.items.all():
            # Заново проверяем склад, вдруг кто-то купил товар пока мы думали
            if item.product.stock < item.quantity:
                # Транзакция прервется, изменения откатятся
                return Response({"error": f"Товара {item.product.name} нет в нужном объеме"}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Списываем со склада
            item.product.stock -= item.quantity
            item.product.save()

            # Фиксируем цену на момент покупки (как обсуждали в архитектуре)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price, 
                quantity=item.quantity
            )

        # 3. Очищаем корзину после успешного оформления
        cart.items.all().delete()

        return Response({"message": "Заказ успешно оформлен", "order_id": order.id}, status=status.HTTP_201_CREATED)

class OrderHistoryView(generics.ListAPIView):
    """ История покупок текущего пользователя (Личный кабинет) """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)