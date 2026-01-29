import pandas as pd
import logging

class MetricsCalculator:
    """Класс для расчёта метрик продаж"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_kpi(self, df: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("Расчёт KPI для каждой строки продаж")
        
        # Создаем копию для безопасной обработки
        df_with_kpi = df.copy()
        
        # Расчёт выручки: qty * price * (1 - discount)
        df_with_kpi['revenue'] = (
            df_with_kpi['qty'] * 
            df_with_kpi['price'] * 
            (1 - df_with_kpi['discount'])
        ).round(2)
        
        # Расчёт прибыли: revenue - qty * cost
        df_with_kpi['profit'] = (
            df_with_kpi['revenue'] - 
            df_with_kpi['qty'] * df_with_kpi['cost']
        ).round(2)
        
        # Проверка расчётов
        negative_profit = (df_with_kpi['profit'] < 0).sum()
        if negative_profit > 0:
            self.logger.warning(f"Обнаружено {negative_profit} строк с отрицательной прибылью")
        
        self.logger.info(f"Средняя выручка на строку: {df_with_kpi['revenue'].mean():.2f}")
        self.logger.info(f"Средняя прибыль на строку: {df_with_kpi['profit'].mean():.2f}")
        
        return df_with_kpi
    
    def calculate_daily_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Расчёт метрик по дням")
        
        # Группировка по дням
        daily_metrics = df.groupby('date').agg({
            'order_id': 'nunique',  # Уникальные заказы
            'revenue': 'sum',
            'profit': 'sum',
            'qty': 'sum'
        }).reset_index()
        
        # Переименование колонок
        daily_metrics.columns = ['date', 'total_orders', 'total_revenue', 
                                'total_profit', 'total_qty']
        
        # Расчёт среднего чека
        daily_metrics['avg_check'] = (
            daily_metrics['total_revenue'] / daily_metrics['total_orders']
        ).round(2)
        
        # Сортировка по дате
        daily_metrics = daily_metrics.sort_values('date')
        
        self.logger.info(f"Рассчитано метрик для {len(daily_metrics)} дней")
        self.logger.info(f"Общая выручка за период: {daily_metrics['total_revenue'].sum():.2f}")
        self.logger.info(f"Общая прибыль за период: {daily_metrics['total_profit'].sum():.2f}")
        
        return daily_metrics
    
    def calculate_store_metrics(self, df: pd.DataFrame, stores_df: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("Расчёт метрик по магазинам")
        
        # Группировка продаж по магазинам
        store_sales = df.groupby('store_id').agg({
            'order_id': 'nunique',
            'revenue': 'sum',
            'profit': 'sum',
            'qty': 'sum'
        }).reset_index()
        
        store_sales.columns = ['store_id', 'orders_count', 'total_revenue', 
                              'total_profit', 'total_qty']
        
        # Находим топовую категорию для каждого магазина
        top_categories = self._get_top_categories_per_store(df)
        
        # Объединяем с данными магазинов
        store_metrics = pd.merge(store_sales, stores_df, on='store_id', how='left')
        store_metrics = pd.merge(store_metrics, top_categories, on='store_id', how='left')
        
        # Сортировка по выручке
        store_metrics = store_metrics.sort_values('total_revenue', ascending=False)
        
        self.logger.info(f"Рассчитано метрик для {len(store_metrics)} магазинов")
        
        return store_metrics
    
    def _get_top_categories_per_store(self, df: pd.DataFrame) -> pd.DataFrame:
        """Находит топовую категорию по выручке для каждого магазина"""
        # Группируем по магазину и категории
        store_categories = df.groupby(['store_id', 'category']).agg({
            'revenue': 'sum'
        }).reset_index()
        
        # Находим категорию с максимальной выручкой для каждого магазина
        top_categories = store_categories.loc[
            store_categories.groupby('store_id')['revenue'].idxmax()
        ][['store_id', 'category']]
        
        top_categories.columns = ['store_id', 'top_category']
        
        return top_categories
    
    def calculate_top_products(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:

        self.logger.info(f"Расчёт топ-{top_n} товаров по выручке")
        
        # Группируем по товарам
        product_metrics = df.groupby(['product_id', 'product_name', 'category']).agg({
            'revenue': 'sum',
            'profit': 'sum',
            'qty': 'sum'
        }).reset_index()
        
        product_metrics.columns = ['product_id', 'product_name', 'category', 
                                  'revenue', 'profit', 'qty_sum']
        
        top_products = product_metrics.sort_values('revenue', ascending=False).head(top_n)
        
        self.logger.info(f"Товар №1 по выручке: {top_products.iloc[0]['product_name']} "
                        f"({top_products.iloc[0]['revenue']:.2f})")
        
        return top_products
    
    def calculate_category_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
 
        self.logger.info("Расчёт метрик по категориям")
        
        # Группируем по категориям
        category_metrics = df.groupby('category').agg({
            'revenue': 'sum',
            'profit': 'sum',
            'qty': 'sum',
            'product_id': 'nunique'
        }).reset_index()
        
        category_metrics.columns = ['category', 'revenue', 'profit', 
                                   'total_qty', 'unique_products']
        
        # Расчёт доли выручки
        total_revenue = category_metrics['revenue'].sum()
        category_metrics['share_revenue'] = (
            category_metrics['revenue'] / total_revenue * 100
        ).round(2)
        
        # Сортировка по выручке
        category_metrics = category_metrics.sort_values('revenue', ascending=False)
        
        self.logger.info(f"Рассчитано метрик для {len(category_metrics)} категорий")
        self.logger.info(f"Топ-3 категории: {', '.join(category_metrics.head(3)['category'].tolist())}")
        
        return category_metrics