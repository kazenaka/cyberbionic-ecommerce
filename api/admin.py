from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Order, OrderItem

# 1. Управление клиентами
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Добавляем наши поля в отображение списка
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    search_fields = ('email', 'first_name', 'phone_number')
    ordering = ('email',)

# 2. Управление категориями
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    # Автоматически заполнять slug на основе названия
    prepopulated_fields = {'slug': ('name',)} 

# 3. Управление каталогом товаров
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'category') # Боковая панель фильтрации
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_active') # Позволяет менять цену и остаток прямо в списке!

# 4. Управление заказами
class OrderItemInline(admin.TabularInline):
    """ Эта штука позволит видеть товары прямо внутри формы заказа """
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'get_cost')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'shipping_address')
    inlines = [OrderItemInline] # Подключаем товары внутрь заказа
    
    # Защита от случайного изменения истории
    readonly_fields = ('created_at',)