from rest_framework import serializers
from .models import CustomUser, Category, Product, Cart, CartItem, Order, OrderItem

# ==========================================
# 1. ПОЛЬЗОВАТЕЛИ
# ==========================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'phone_number', 'shipping_address', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 1. Генерируем обязательное поле username из email, 
        # чтобы база данных не ругалась на пустое значение
        validated_data['username'] = validated_data['email']
        
        # 2. Создаем пользователя (пароль захешируется автоматически внутри create_user)
        user = CustomUser.objects.create_user(**validated_data)
        return user


# ==========================================
# 2. КАТАЛОГ ТОВАРОВ
# ==========================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class ProductSerializer(serializers.ModelSerializer):
    """ Сериализатор товара """
    # Добавляем поле category_name, чтобы фронтенд сразу получил строку "Ноутбуки", а не просто ID категории "2"
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_name', 'name', 'description', 
            'price', 'stock', 'image_url', 'is_active', 'created_at'
        )


# ==========================================
# 3. КОРЗИНА 
# ==========================================
class CartItemSerializer(serializers.ModelSerializer):
    # Вкладываем сериализатор продукта, чтобы при запросе корзины фронтенд получил всю инфу о товаре (картинку, цену)
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    # Считаем стоимость одной позиции (цена * количество)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal')

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price')

    def get_total_price(self, obj):
        # Вычисляем общую сумму корзины "на лету"
        return sum(item.product.price * item.quantity for item in obj.items.all())


# ==========================================
# 4. ЗАКАЗЫ (ИСТОРИЯ ПОКУПОК)
# ==========================================
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'price', 'quantity')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'shipping_address', 'created_at', 'items', 'total_cost')

    def get_total_cost(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())