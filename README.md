# 📊 Sales Analytics Dashboard

Автоматическая система аналитики продаж для формирования регулярных отчётов и визуализации ключевых бизнес-метрик.

## 🚀 Возможности

- **Автоматическая обработка данных**: Загрузка, очистка и валидация CSV файлов
- **Расчёт KPI**: Выручка, прибыль, средний чек по бизнес-формулам
- **Генерация отчётов**: 4 типа сводных таблиц (CSV + Excel)
- **Визуализация**: Построение графиков и дашбордов аналитики
- **Логирование**: Детальная трассировка выполнения операций
- **Тестовые данные**: Генератор реалистичных датасетов

## 📋 Технические требования

- Python 3.10+
- Pandas 1.5.0+
- Matplotlib 3.6.0+
- Openpyxl 3.0.0+ (для Excel отчётов)

## 📊 Формат входных данных

1. Файл продаж data/sales.csv
date,store_id,order_id,product_id,product_name,category,qty,price,discount,cost
2024-01-01,S01,ORD1001,P001,Смартфон iPhone 14,Электроника,1,89999.99,0.1,45000
2024-01-01,S01,ORD1001,P002,Наушники AirPods,Электроника,2,19999.99,0,8000

csv
date,store_id,order_id,product_id,product_name,category,qty,price,discount,cost
2024-01-01,S01,ORD1001,P001,Смартфон iPhone 14,Электроника,1,89999.99,0.1,45000
2024-01-01,S01,ORD1001,P002,Наушники AirPods,Электроника,2,19999.99,0,8000

- Обязательные колонки:

- date (YYYY-MM-DD) - дата продажи
- store_id (S01, S02...) - ID магазина
- order_id - номер заказа
- product_id - ID товара
- product_name - название товара
- category - категория товара
- qty (int) - количество
- price (float) - цена за единицу
- discount (float, 0..1) - доля скидки
- cost (float) - себестоимость за 1 шт.

2. Файл магазинов data/stores.csv
- store_id,city,format
- S01,Москва,offline
- S02,Санкт-Петербург,offline
- S03,Online,online

## 📈 Формируемые отчёты

**Отчёт A: Итоги по дням (output/report_daily.csv)**
  
- date - дата
- total_orders - количество заказов
- total_revenue - общая выручка
- total_profit - общая прибыль
- avg_check - средний чек

**Отчёт B: Итоги по магазинам (output/report_stores.csv)**

- store_id, city, format - информация о магазине
- total_revenue - выручка магазина
- total_profit - прибыль магазина
- orders_count - количество заказов
- top_category - топовая категория по выручке

**Отчёт C: Топ товаров (output/report_top_products.csv)**

**Топ-10 товаров по выручке:**

- product_id, product_name, category
- revenue, profit, qty_sum

**Отчёт D: Категории (output/report_categories.csv)**

- category - категория товара
- revenue - выручка по категории
- profit - прибыль по категории
- share_revenue - доля выручки от общей

## 📊 Визуализации
**Система автоматически строит и сохраняет в папку charts/:**

- Выручка по дням (daily_revenue.png) - линейный график динамики
- Прибыль по дням (daily_profit.png) - линейный график с выделением убытков
- Топ категорий (top_categories.png) - барчарт и круговая диаграмма
- Дашборд аналитики (sales_dashboard.png) - сводная информация на одном изображении
