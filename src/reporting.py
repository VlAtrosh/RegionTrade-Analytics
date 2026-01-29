import pandas as pd
import logging
from pathlib import Path
import os

class ReportGenerator:
    """Класс для генерации отчётов"""
    
    def __init__(self, output_dir: str = 'output'):
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        
        # Создаем папку для отчётов если её нет
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_all_reports(self, df: pd.DataFrame, stores_df: pd.DataFrame, 
                           daily_metrics: pd.DataFrame, store_metrics: pd.DataFrame,
                           top_products: pd.DataFrame, category_metrics: pd.DataFrame):

        self.logger.info("Генерация всех отчётов")
        
        # Генерация отдельных отчётов
        self.save_daily_report(daily_metrics)
        self.save_stores_report(store_metrics)
        self.save_top_products_report(top_products)
        self.save_categories_report(category_metrics)
        
        # Генерация сводного отчёта в Excel
        self.save_summary_excel(daily_metrics, store_metrics, top_products, category_metrics)
        
        self.logger.info("Все отчёты успешно сгенерированы")
    
    def save_daily_report(self, daily_metrics: pd.DataFrame):
        """Сохраняет отчёт по дням"""
        filepath = Path(self.output_dir) / 'report_daily.csv'
        
        # Форматирование даты для сохранения
        report_df = daily_metrics.copy()
        report_df['date'] = report_df['date'].dt.strftime('%Y-%m-%d')
        
        report_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        self.logger.info(f"Отчёт по дням сохранён: {filepath}")
        
        return filepath
    
    def save_stores_report(self, store_metrics: pd.DataFrame):
        """Сохраняет отчёт по магазинам"""
        filepath = Path(self.output_dir) / 'report_stores.csv'
        
        # Выбираем нужные колонки и сортируем
        report_df = store_metrics[[
            'store_id', 'city', 'format', 'total_revenue', 
            'total_profit', 'orders_count', 'top_category'
        ]].copy()
        
        report_df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"Отчёт по магазинам сохранён: {filepath}")
        
        return filepath
    
    def save_top_products_report(self, top_products: pd.DataFrame):
        """Сохраняет отчёт по топ товарам"""
        filepath = Path(self.output_dir) / 'report_top_products.csv'
        
        # Убеждаемся, что у нас топ-10
        report_df = top_products.head(10).copy()
        
        report_df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"Отчёт по топ товарам сохранён: {filepath}")
        
        return filepath
    
    def save_categories_report(self, category_metrics: pd.DataFrame):
        """Сохраняет отчёт по категориям"""
        filepath = Path(self.output_dir) / 'report_categories.csv'
        
        # Форматируем проценты
        report_df = category_metrics.copy()
        
        report_df.to_csv(filepath, index=False, encoding='utf-8')
        self.logger.info(f"Отчёт по категориям сохранён: {filepath}")
        
        return filepath
    
    def save_summary_excel(self, daily_metrics: pd.DataFrame, store_metrics: pd.DataFrame,
                          top_products: pd.DataFrame, category_metrics: pd.DataFrame):
        """Сохраняет сводный отчёт в Excel"""
        try:
            filepath = Path(self.output_dir) / 'summary_report.xlsx'
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Лист с итогами по дням
                daily_report = daily_metrics.copy()
                daily_report['date'] = daily_report['date'].dt.strftime('%Y-%m-%d')
                daily_report.to_excel(writer, sheet_name='По дням', index=False)
                
                # Лист с магазинами
                store_report = store_metrics[[
                    'store_id', 'city', 'format', 'total_revenue', 
                    'total_profit', 'orders_count', 'top_category'
                ]].copy()
                store_report.to_excel(writer, sheet_name='По магазинам', index=False)
                
                # Лист с топ товарами
                top_products.head(10).to_excel(writer, sheet_name='Топ товары', index=False)
                
                # Лист с категориями
                category_metrics.to_excel(writer, sheet_name='По категориям', index=False)
                
                # Лист с итоговой сводкой
                self._create_summary_sheet(writer, daily_metrics, store_metrics, 
                                          category_metrics)
            
            self.logger.info(f"Сводный Excel отчёт сохранён: {filepath}")
            return filepath
            
        except ImportError:
            self.logger.warning("openpyxl не установлен, Excel отчёт не будет создан")
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при создании Excel отчёта: {str(e)}")
            return None
    
    def _create_summary_sheet(self, writer, daily_metrics, store_metrics, category_metrics):
        summary_data = {
            'Показатель': [
                'Период анализа',
                'Всего дней',
                'Общая выручка',
                'Общая прибыль',
                'Средний чек',
                'Всего заказов',
                'Всего продано товаров',
                'Количество магазинов',
                'Топовая категория',
                'Лучший магазин по выручке',
                'Худший магазин по выручке'
            ],
            'Значение': [
                f"{daily_metrics['date'].min().strftime('%d.%m.%Y')} - "
                f"{daily_metrics['date'].max().strftime('%d.%m.%Y')}",
                len(daily_metrics),
                f"{daily_metrics['total_revenue'].sum():,.2f}",
                f"{daily_metrics['total_profit'].sum():,.2f}",
                f"{(daily_metrics['total_revenue'].sum() / daily_metrics['total_orders'].sum()):.2f}",
                int(daily_metrics['total_orders'].sum()),
                int(daily_metrics['total_qty'].sum()),
                len(store_metrics),
                category_metrics.iloc[0]['category'],
                store_metrics.iloc[0]['store_id'] if len(store_metrics) > 0 else 'N/A',
                store_metrics.iloc[-1]['store_id'] if len(store_metrics) > 0 else 'N/A'
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Сводка', index=False)
        
        # Автоматическая настройка ширины колонок
        worksheet = writer.sheets['Сводка']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def print_console_summary(self, daily_metrics: pd.DataFrame, store_metrics: pd.DataFrame,
                            category_metrics: pd.DataFrame):
        """Выводит краткую сводку в консоль"""
        print("\n" + "="*50)
        print(" ОТЧЁТ ПО ПРОДАЖАМ".center(50))
        print("="*50)
        
        # Общая информация
        total_revenue = daily_metrics['total_revenue'].sum()
        total_profit = daily_metrics['total_profit'].sum()
        total_orders = daily_metrics['total_orders'].sum()
        avg_check = total_revenue / total_orders if total_orders > 0 else 0
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   Период: {daily_metrics['date'].min().strftime('%d.%m.%Y')} - "
              f"{daily_metrics['date'].max().strftime('%d.%m.%Y')}")
        print(f"   Всего выручка: {total_revenue:,.2f} руб.")
        print(f"   Всего прибыль: {total_profit:,.2f} руб.")
        print(f"   Средний чек: {avg_check:.2f} руб.")
        print(f"   Всего заказов: {total_orders}")
        
        # Топ магазины
        print(f"\n🏪 ТОП-3 МАГАЗИНА ПО ВЫРУЧКЕ:")
        for i in range(min(3, len(store_metrics))):
            store = store_metrics.iloc[i]
            print(f"   {i+1}. {store['store_id']} ({store['city']}, {store['format']}) - "
                  f"{store['total_revenue']:,.2f} руб.")
        
        # Топ категории
        print(f"\n ТОП-3 КАТЕГОРИИ:")
        for i in range(min(3, len(category_metrics))):
            category = category_metrics.iloc[i]
            print(f"   {i+1}. {category['category']} - "
                  f"{category['share_revenue']}% ({category['revenue']:,.2f} руб.)")
        
        # Дополнительная информация
        print(f"\n ДОПОЛНИТЕЛЬНО:")
        print(f"   Магазинов всего: {len(store_metrics)}")
        print(f"   Категорий товаров: {len(category_metrics)}")
        print(f"   Средняя маржинальность: {(total_profit / total_revenue * 100 if total_revenue > 0 else 0):.1f}%")
        
        print("\n" + "="*50)
        print("Отчёты сохранены в папке 'output/'".center(50))
        print("="*50 + "\n")