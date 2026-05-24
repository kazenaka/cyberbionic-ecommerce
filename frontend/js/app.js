const App = {
    root: document.getElementById('app-root'),
    
    showLoader() {
        this.root.innerHTML = `
            <div class="flex justify-center items-center h-64">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>`;
    },

    updateHeader() {
        const isAuth = !!localStorage.getItem('access_token');
        document.getElementById('auth-guest').classList.toggle('hidden', isAuth);
        document.getElementById('auth-user').classList.toggle('hidden', !isAuth);
        document.getElementById('auth-user').classList.toggle('flex', isAuth);
    },

    async router() {
        this.showLoader();
        this.updateHeader();

        const hash = window.location.hash.slice(1) || 'catalog';

        switch (hash) {
            case 'catalog': await this.renderCatalog(); break;
            case 'cart': await this.renderCart(); break;
            case 'login': this.renderLogin(); break;
            case 'register': this.renderRegister(); break;
            case 'profile': await this.renderProfile(); break;
            default: this.root.innerHTML = Components.EmptyState('Страница не найдена 404');
        }
    },

    async renderCatalog() {
        const products = await API.getProducts();
        if (!products) {
            this.root.innerHTML = Components.EmptyState('Не удалось загрузить товары');
            return;
        }

        let html = `
            <h1 class="text-3xl font-bold mb-8 text-gray-800">Каталог товаров</h1>
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        `;
        
        products.forEach(p => html += Components.ProductCard(p));
        html += `</div>`;
        this.root.innerHTML = html;
    },

    renderLogin() {
        this.root.innerHTML = `
            <div class="max-w-md mx-auto bg-white p-8 rounded-xl shadow-sm mt-10">
                <h2 class="text-2xl font-bold mb-6 text-center">Вход в систему</h2>
                <form id="login-form" class="flex flex-col gap-4">
                    <input type="email" id="email" placeholder="Email" class="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <input type="password" id="password" placeholder="Пароль" class="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <button type="submit" class="bg-blue-500 text-white py-2 rounded font-bold hover:bg-blue-600 transition">Войти</button>
                </form>
                <div class="mt-4 text-center text-sm text-gray-600">
                    Нет аккаунта? <a href="#register" class="text-blue-500 hover:underline">Зарегистрироваться</a>
                </div>
            </div>
        `;

        document.getElementById('login-form').onsubmit = async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const response = await API.login({ email, password });
            if (response && response.access) {
                localStorage.setItem('access_token', response.access);
                window.location.hash = '#catalog';
            }
        };
    },

    renderRegister() {
        this.root.innerHTML = `
            <div class="max-w-md mx-auto bg-white p-8 rounded-xl shadow-sm mt-10">
                <h2 class="text-2xl font-bold mb-6 text-center">Регистрация</h2>
                <form id="register-form" class="flex flex-col gap-4">
                    <input type="text" id="reg-name" placeholder="Ваше имя" class="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <input type="email" id="reg-email" placeholder="Email *" class="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <input type="password" id="reg-password" placeholder="Пароль *" class="border p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <button type="submit" class="bg-green-500 text-white py-2 rounded font-bold hover:bg-green-600 transition">Создать аккаунт</button>
                </form>
                <div class="mt-4 text-center text-sm text-gray-600">
                    Уже есть аккаунт? <a href="#login" class="text-blue-500 hover:underline">Войти</a>
                </div>
            </div>
        `;

        document.getElementById('register-form').onsubmit = async (e) => {
            e.preventDefault();
            const first_name = document.getElementById('reg-name').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            
            const response = await API.register({ first_name, email, password });
            if (response && response.email) {
                alert('Регистрация успешна! Теперь вы можете войти.');
                window.location.hash = '#login';
            }
        };
    },

    async renderCart() {
        if (!localStorage.getItem('access_token')) {
            window.location.hash = '#login';
            return;
        }

        const cartData = await API.getCart();
        
        if (!cartData || !cartData.items || cartData.items.length === 0) {
            this.root.innerHTML = `
                <div class="text-center py-16">
                    <h2 class="text-2xl font-bold text-gray-700 mb-2">Ваша корзина пуста</h2>
                    <p class="text-gray-500 mb-6">Самое время добавить в нее что-нибудь из каталога.</p>
                    <a href="#catalog" class="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition">Перейти в каталог</a>
                </div>
            `;
            return;
        }

        let html = `
            <div class="max-w-4xl mx-auto">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold text-gray-800">Корзина</h1>
                    <button id="clear-cart-btn" class="text-red-500 hover:text-red-700 text-sm font-medium transition">Очистить корзину</button>
                </div>
                <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-6">
        `;
        
        cartData.items.forEach(item => {
            html += Components.CartItemRow(item);
        });

        html += `
                </div>
                <div class="text-right mb-4">
                    <span class="text-gray-600">Итого к оплате:</span>
                    <span class="text-2xl font-black text-gray-900 ml-2">${cartData.total_price} $</span>
                </div>
        `;

        html += Components.CheckoutForm();
        html += `</div>`;

        this.root.innerHTML = html;

        document.getElementById('clear-cart-btn').onclick = async () => {
            if(confirm('Вы уверены, что хотите удалить все товары?')) {
                await API.clearCart();
                this.renderCart();
            }
        };

        document.getElementById('checkout-form').onsubmit = async (e) => {
            e.preventDefault();
            const name = document.getElementById('order-name').value;
            const email = document.getElementById('order-email').value;
            const phone = document.getElementById('order-phone').value;
            const address = document.getElementById('order-address').value;

            const combinedAddress = `Получатель: ${name}, Email: ${email}, Тел: ${phone}. Адрес: ${address}`;
            const response = await API.checkout({ shipping_address: combinedAddress });
            
            if (response && response.order_id) {
                this.root.innerHTML = `
                    <div class="text-center py-20 max-w-lg mx-auto">
                        <h2 class="text-3xl font-bold text-gray-800 mb-2">Заказ #${response.order_id} оформлен!</h2>
                        <p class="text-gray-600 mb-8">Спасибо за покупку. Мы свяжемся с вами в ближайшее время для подтверждения.</p>
                        <a href="#catalog" class="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition font-bold shadow-lg">Вернуться к покупкам</a>
                    </div>
                `;
            }
        };
    },

    async renderProfile() {
        if (!localStorage.getItem('access_token')) {
            window.location.hash = '#login';
            return;
        }

        const [profile, orders] = await Promise.all([
            API.getProfile(),
            API.getOrders()
        ]);

        if (!profile) return;

        let html = `
            <div class="max-w-4xl mx-auto">
                <h1 class="text-3xl font-bold text-gray-800 mb-8">Личный кабинет</h1>
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8 flex items-center gap-6">
                    <div class="w-20 h-20 bg-blue-100 text-blue-500 rounded-full flex items-center justify-center text-3xl font-bold">
                        ${profile.email.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 class="text-xl font-bold text-gray-900">${profile.first_name || 'Пользователь'}</h2>
                        <p class="text-gray-600">${profile.email}</p>
                    </div>
                </div>
                <h3 class="text-2xl font-bold text-gray-800 mb-4">История заказов</h3>
        `;

        if (!orders || orders.length === 0) {
            html += Components.EmptyState('Вы еще ничего не заказывали');
        } else {
            html += `<div class="flex flex-col gap-4">`;
            orders.forEach(order => {
                const statusLabels = {
                    'pending': 'В обработке', 'paid': 'Оплачен', 
                    'shipped': 'Отправлен', 'delivered': 'Доставлен', 'cancelled': 'Отменен'
                };

                html += `
                    <div class="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                        <div class="flex justify-between items-center border-b pb-3 mb-3">
                            <span class="font-bold text-gray-800">Заказ #${order.id} <span class="text-sm text-gray-500 font-normal ml-2">от ${new Date(order.created_at).toLocaleDateString()}</span></span>
                            <span class="px-3 py-1 rounded-full text-xs font-bold bg-gray-100">${statusLabels[order.status] || order.status}</span>
                        </div>
                        <ul class="text-sm text-gray-600 space-y-2">
                            ${order.items.map(item => `
                                <li class="flex justify-between">
                                    <span>${item.product_name} <span class="text-gray-400">x${item.quantity}</span></span>
                                    <span class="font-medium">${(item.price * item.quantity).toFixed(2)} $</span>
                                </li>
                            `).join('')}
                        </ul>
                        <div class="text-right mt-4 pt-3 border-t font-bold text-gray-900 text-lg">Итого: ${order.total_cost} $</div>
                    </div>
                `;
            });
            html += `</div>`;
        }
        html += `</div>`;
        this.root.innerHTML = html;
    },

    async addToCart(productId) {
        if (!localStorage.getItem('access_token')) {
            alert('Пожалуйста, войдите в систему, чтобы добавлять товары в корзину');
            window.location.hash = '#login';
            return;
        }
        await API.addToCart(productId, 1);
        alert('Товар добавлен в корзину!');
    },

    logout() {
        localStorage.removeItem('access_token');
        window.location.hash = '#login';
        this.updateHeader();
    }
};

window.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('hashchange', () => App.router());
    document.getElementById('logout-btn').addEventListener('click', () => App.logout());
    App.router();
});