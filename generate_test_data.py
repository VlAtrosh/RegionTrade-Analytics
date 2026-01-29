"""
Генератор тестовых данных для аналитики продаж
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_test_data(num_sales=1000, num_stores=6, num_products=30):
    """Генерирует тестовые данные продаж и магазинов"""
    
    # Создаем папку data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Генерация данных магазинов
    stores_data = generate_stores_data(num_stores)
    
    # Генерация данных товаров
    products_data = generate_products_data(num_products)
    
    # Генерация данных продаж
    sales_data = generate_sales_data(num_sales, stores_data, products_data)
    
    # Сохранение данных
    stores_df = pd.DataFrame(stores_data)
    sales_df = pd.DataFrame(sales_data)
    
    stores_df.to_csv('data/stores.csv', index=False, encoding='utf-8-sig')
    sales_df.to_csv('data/sales.csv', index=False, encoding='utf-8-sig')
    
    print(f"✅ Сгенерировано:")
    print(f"   - {num_stores} магазинов в data/stores.csv")
    print(f"   - {num_sales} продаж в data/sales.csv")
    print(f"   - {num_products} уникальных товаров")
    
    return stores_df, sales_df

def generate_stores_data(num_stores):
    """Генерирует данные магазинов"""
    cities = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 
              'Казань', 'Нижний Новгород', 'Краснодар', 'Воронеж']
    formats = ['offline', 'online']
    
    stores = []
    for i in range(1, num_stores + 1):
        store_id = f"S{i:02d}"
        city = random.choice(cities)
        store_format = random.choice(formats)
        
        # Для онлайн магазинов убираем город
        if store_format == 'online':
            city = 'Online'
        
        stores.append({
            'store_id': store_id,
            'city': city,
            'format': store_format
        })
    
    return stores

def generate_products_data(num_products):
    """Генерирует данные товаров"""
    categories = ['Электроника', 'Одежда', 'Книги', 'Продукты', 
                  'Косметика', 'Спорттовары', 'Мебель', 'Игрушки']
    
    electronic_names = ['Смартфон', 'Ноутбук', 'Наушники', 'Планшет', 'Умные часы']
    clothes_names = ['Футболка', 'Джинсы', 'Куртка', 'Платье', 'Обувь']
    books_names = ['Роман', 'Учебник', 'Детектив', 'Фэнтези', 'Бизнес-литература']
    food_names = ['Молоко', 'Хлеб', 'Сыр', 'Фрукты', 'Кондитерские изделия']
    cosmetics_names = ['Крем', 'Шампунь', 'Помада', 'Тушь', 'Духи']
    sports_names = ['Мяч', 'Гантели', 'Коврик', 'Велосипед', 'Ракетка']
    furniture_names = ['Стул', 'Стол', 'Диван', 'Кровать', 'Шкаф']
    toys_names = ['Конструктор', 'Кукла', 'Машинка', 'Пазл', 'Мягкая игрушка']
    
    all_names = electronic_names + clothes_names + books_names + food_names + \
                cosmetics_names + sports_names + furniture_names + toys_names
    
    products = []
    used_names = set()
    
    for i in range(1, num_products + 1):
        product_id = f"P{i:03d}"
        
        # Выбираем категорию и соответствующее имя
        category = random.choice(categories)
        
        if category == 'Электроника':
            name_base = random.choice(electronic_names)
        elif category == 'Одежда':
            name_base = random.choice(clothes_names)
        elif category == 'Книги':
            name_base = random.choice(books_names)
        elif category == 'Продукты':
            name_base = random.choice(food_names)
        elif category == 'Косметика':
            name_base = random.choice(cosmetics_names)
        elif category == 'Спорттовары':
            name_base = random.choice(sports_names)
        elif category == 'Мебель':
            name_base = random.choice(furniture_names)
        elif category == 'Игрушки':
            name_base = random.choice(toys_names)
        else:
            name_base = random.choice(all_names)
        
        # Делаем имя уникальным
        name = f"{name_base} {random.randint(1, 1000)}"
        while name in used_names:
            name = f"{name_base} {random.randint(1, 1000)}"
        used_names.add(name)
        
        # Генерируем себестоимость и цену
        if category == 'Электроника':
            cost = round(random.uniform(100, 1000), 2)
            price = round(cost * random.uniform(1.2, 2.0), 2)
        elif category == 'Одежда':
            cost = round(random.uniform(20, 200), 2)
            price = round(cost * random.uniform(1.5, 3.0), 2)
        else:
            cost = round(random.uniform(10, 100), 2)
            price = round(cost * random.uniform(1.3, 2.5), 2)
        
        products.append({
            'product_id': product_id,
            'product_name': name,
            'category': category,
            'base_cost': cost,
            'base_price': price
        })
    
    return products

def generate_sales_data(num_sales, stores_data, products_data):
    """Генерирует данные продаж"""
    
    # Начальная дата - 30 дней назад
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    sales = []
    order_counter = 1000
    
    # Создаем словари для быстрого доступа
    store_ids = [store['store_id'] for store in stores_data]
    
    for i in range(num_sales):
        # Генерируем дату
        date_delta = random.randint(0, 30)
        sale_date = start_date + timedelta(days=date_delta)
        
        # Выбираем магазин и товар
        store_id = random.choice(store_ids)
        product = random.choice(products_data)
        
        # Генерируем количество (иногда с ошибкой - отрицательное)
        if random.random() < 0.02:  # 2% ошибок
            qty = random.randint(-5, -1)  # Отрицательное количество
        else:
            qty = random.randint(1, 10)
        
        # Генерируем цену с возможной ошибкой
        if random.random() < 0.01:  # 1% ошибок
            price = round(product['base_price'] * random.uniform(-0.5, 0), 2)
        else:
            price = round(product['base_price'] * random.uniform(0.9, 1.1), 2)
        
        # Генерируем скидку (иногда с ошибкой)
        if random.random() < 0.03:  # 3% ошибок
            discount = round(random.uniform(-0.2, 1.5), 2)
        else:
            discount = round(random.uniform(0, 0.3), 2)
        
        # Генерируем себестоимость
        cost = product['base_cost']
        
        # Иногда добавляем пропуск категории
        category = product['category']
        if random.random() < 0.05:  # 5% пропусков
            category = None
        
        # Создаем заказ - несколько позиций в одном заказе
        if i % random.randint(2, 5) == 0:
            order_counter += 1
        
        sales.append({
            'date': sale_date.strftime('%Y-%m-%d'),
            'store_id': store_id,
            'order_id': f"ORD{order_counter}",
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'category': category,
            'qty': qty,
            'price': price,
            'discount': discount,
            'cost': cost
        })
    
    return sales

if __name__ == "__main__":
    # Генерация данных с параметрами по умолчанию
    generate_test_data()