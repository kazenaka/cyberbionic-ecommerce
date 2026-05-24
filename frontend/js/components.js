const Components = {
    // Карточка товара
    ProductCard: (product) => `
        <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition duration-300 overflow-hidden flex flex-col">
            <div class="h-48 bg-gray-200 w-full object-cover">
                ${product.image_url 
                    ? `<img src="${product.image_url}" alt="${product.name}" class="h-full w-full object-cover">` 
                    : `<div class="flex items-center justify-center h-full text-gray-400">Нет фото</div>`
                }
            </div>
            <div class="p-5 flex flex-col flex-grow">
                <span class="text-xs font-semibold text-blue-500 uppercase mb-1">${product.category_name || ''}</span>
                <h3 class="text-lg font-bold text-gray-800 mb-2">${product.name}</h3>
                <p class="text-gray-600 text-sm mb-4 line-clamp-2">${product.description || 'Описание отсутствует'}</p>
                <div class="mt-auto flex justify-between items-center">
                    <span class="text-xl font-extrabold text-gray-900">${product.price} ₽</span>
                    ${product.stock > 0 
                        ? `<button onclick="App.addToCart(${product.id})" class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-lg transition" title="В корзину">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                           </button>`
                        : `<span class="text-red-500 text-sm font-bold">Нет в наличии</span>`
                    }
                </div>
            </div>
        </div>
    `,

    // Пустое состояние
    EmptyState: (message) => `
        <div class="text-center py-12">
            <h2 class="text-2xl text-gray-500">${message}</h2>
        </div>
    `,

    // Строка корзины
    CartItemRow: (item) => `
        <div class="flex items-center justify-between p-4 border-b border-gray-100 hover:bg-gray-50 transition">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 bg-gray-200 rounded-md overflow-hidden flex-shrink-0">
                    ${item.product.image_url 
                        ? `<img src="${item.product.image_url}" alt="${item.product.name}" class="w-full h-full object-cover">`
                        : `<div class="w-full h-full flex items-center justify-center text-xs text-gray-400">Нет фото</div>`
                    }
                </div>
                <div>
                    <h4 class="text-gray-800 font-semibold">${item.product.name}</h4>
                    <p class="text-sm text-gray-500">${item.product.price} ₽ x ${item.quantity}</p>
                </div>
            </div>
            <div class="text-lg font-bold text-gray-900">
                ${item.subtotal} ₽
            </div>
        </div>
    `,

    // Форма оформления заказа
    CheckoutForm: () => `
        <div class="bg-gray-50 p-6 rounded-xl border border-gray-200 mt-8">
            <h3 class="text-xl font-bold text-gray-800 mb-4">Данные получателя и доставка</h3>
            <form id="checkout-form" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600 font-medium">ФИО получателя *</label>
                    <input type="text" id="order-name" required class="border p-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none">
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600 font-medium">Email получателя *</label>
                    <input type="email" id="order-email" required class="border p-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none">
                </div>
                <div class="flex flex-col gap-1">
                    <label class="text-sm text-gray-600 font-medium">Телефон *</label>
                    <input type="tel" id="order-phone" required class="border p-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none">
                </div>
                <div class="flex flex-col gap-1 md:col-span-2">
                    <label class="text-sm text-gray-600 font-medium">Полный адрес доставки *</label>
                    <textarea id="order-address" rows="2" required class="border p-2 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"></textarea>
                </div>
                
                <div class="md:col-span-2 mt-4">
                    <button type="submit" class="w-full bg-green-500 text-white font-bold py-3 rounded-lg hover:bg-green-600 transition shadow-lg text-lg">
                        Подтвердить заказ
                    </button>
                </div>
            </form>
        </div>
    `
};