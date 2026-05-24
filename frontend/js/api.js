// Проверяем, запущен ли сайт на локальном компьютере
const isLocalhost = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost';

// Если локально - стучимся в локальный Django. Если в интернете - стучимся на Render.
const API_BASE_URL = isLocalhost 
    ? 'http://127.0.0.1:8000/api/v1' 
    : 'https://cybershop-api-sdyt.onrender.com/api/v1';

const API = {
    // Получение токена из LocalStorage
    getToken: () => localStorage.getItem('access_token'),

    // Базовый метод для запросов
    async request(endpoint, method = 'GET', body = null) {
        const headers = {
            'Content-Type': 'application/json',
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`; 
        }

        const config = { method, headers };
        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.hash = '#login';
                return null;
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || errorData.error || 'Ошибка API');
            }
            
            if (response.status === 204) return true; 

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            alert(error.message); 
            return null;
        }
    },

    // Бизнес-логика (обрати внимание на запятые в конце каждой строки)
    getProducts: (queryString = '') => API.request(`/products/${queryString}`),
    register: (userData) => API.request('/register/', 'POST', userData),
    login: (credentials) => API.request('/login/', 'POST', credentials),
    getProfile: () => API.request('/profile/'),
    getOrders: () => API.request('/orders/'),
    getCart: () => API.request('/cart/'),
    addToCart: (product_id, quantity = 1) => API.request('/cart/', 'POST', { product_id, quantity }),
    clearCart: () => API.request('/cart/', 'DELETE'),
    checkout: (orderData) => API.request('/checkout/', 'POST', orderData)
};