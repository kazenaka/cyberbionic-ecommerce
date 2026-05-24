from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

# ==========================================
# 1. ПОЛЬЗОВАТЕЛИ
# ==========================================
class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя. Наследуемся от AbstractUser,
    чтобы сохранить логику аутентификации Django, но добавить нужные нам поля.
    В settings.py обязательно укажем: AUTH_USER_MODEL = 'имя_приложения.CustomUser'
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    shipping_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес доставки")

    # Переопределяем поле USERNAME_FIELD, чтобы пользователь мог логиниться по email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username остается для совместимости с админкой

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


# ==========================================
# 2. КАТАЛОГ ТОВАРОВ
# ==========================================
class Category(models.Model):
    """ Категории товаров для фильтрации """
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-псевдоним")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """ Модель товара """
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    # DecimalField подходит для денег, исключает ошибки округления float
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name="Цена"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток на складе")
    
    # Для MVP просто URL картинки, чтобы не возиться с облачными хранилищами
    image_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на изображение")
    
    is_active = models.BooleanField(default=True, verbose_name="Активен (в продаже)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ==========================================
# 3. КОРЗИНА И ЗАКАЗЫ
# ==========================================
class Cart(models.Model):
    """ Корзина пользователя. Одна корзина — один пользователь. """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    """ Товары внутри корзины """
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        # Один и тот же товар не должен дублироваться в корзине, мы просто увеличиваем quantity
        unique_together = ('cart', 'product') 

class Order(models.Model):
    """ Оформленный заказ для истории покупок """
    STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(CustomUser, related_name='orders', on_delete=models.CASCADE, verbose_name="Клиент")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заказа")
    shipping_address = models.CharField(max_length=255, verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.email}"

class OrderItem(models.Model):
    """ 
    Товары внутри заказа. 
    Архитектурно ВАЖНО: мы копируем цену (price) из Product на момент создания заказа.
    Если завтра цена товара изменится в каталоге, в старых чеках (истории покупок) 
    она должна остаться прежней. 
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200) # Сохраняем имя на случай, если товар удалят из БД
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity