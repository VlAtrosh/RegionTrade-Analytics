import pandas as pd
import logging
import numpy as np

class DataCleaner:
    """Класс для очистки данных продаж"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cleaning_stats = {
            'initial_rows': 0,
            'final_rows': 0,
            'removed_rows': 0,
            'fixed_values': 0,
            'issues_found': {}
        }
    
    def clean_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("Начало очистки данных продаж")
        self.cleaning_stats['initial_rows'] = len(df)
        
        df_clean = df.copy()
        
        df_clean = self._fix_dates(df_clean)
        
        df_clean = self._handle_missing_values(df_clean)
        
        df_clean = self._fix_invalid_values(df_clean)

        df_clean = self._remove_duplicates(df_clean)
        
        df_clean = self._remove_invalid_rows(df_clean)
        
        self.cleaning_stats['final_rows'] = len(df_clean)
        self.cleaning_stats['removed_rows'] = self.cleaning_stats['initial_rows'] - self.cleaning_stats['final_rows']
        
        self.logger.info(f"Очистка завершена:")
        self.logger.info(f"  Изначально строк: {self.cleaning_stats['initial_rows']}")
        self.logger.info(f"  После очистки: {self.cleaning_stats['final_rows']}")
        self.logger.info(f"  Удалено строк: {self.cleaning_stats['removed_rows']}")
        self.logger.info(f"  Исправлено значений: {self.cleaning_stats['fixed_values']}")
        
        if self.cleaning_stats['issues_found']:
            for issue, count in self.cleaning_stats['issues_found'].items():
                self.logger.warning(f"  Обнаружено {count} проблем: {issue}")
        
        return df_clean
    
    def _fix_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Приводит колонку date к типу datetime"""
        try:
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
            invalid_dates = df['date'].isna().sum()
            if invalid_dates > 0:
                self.cleaning_stats['issues_found']['invalid_dates'] = invalid_dates
                self.logger.warning(f"Обнаружено {invalid_dates} некорректных дат")
            return df
        except Exception as e:
            self.logger.error(f"Ошибка при конвертации дат: {str(e)}")
            raise
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'category' in df.columns:
            initial_missing = df['category'].isna().sum()
            df['category'] = df['category'].fillna('Unknown')
            if initial_missing > 0:
                self.cleaning_stats['fixed_values'] += initial_missing
                self.logger.info(f"Заполнено {initial_missing} пропусков в категориях значением 'Unknown'")
        
        return df
    
    def _fix_invalid_values(self, df: pd.DataFrame) -> pd.DataFrame:
        fixes_count = 0
        
        negative_qty_mask = df['qty'] < 0
        if negative_qty_mask.any():
            negative_count = negative_qty_mask.sum()
            df.loc[negative_qty_mask, 'qty'] = abs(df.loc[negative_qty_mask, 'qty'])
            self.cleaning_stats['issues_found']['negative_qty'] = negative_count
            self.logger.warning(f"Исправлено {negative_count} отрицательных количеств")
            fixes_count += negative_count
        
        negative_price_mask = df['price'] < 0
        if negative_price_mask.any():
            negative_count = negative_price_mask.sum()
            df.loc[negative_price_mask, 'price'] = abs(df.loc[negative_price_mask, 'price'])
            self.cleaning_stats['issues_found']['negative_price'] = negative_count
            self.logger.warning(f"Исправлено {negative_count} отрицательных цен")
            fixes_count += negative_count
        
        negative_cost_mask = df['cost'] < 0
        if negative_cost_mask.any():
            negative_count = negative_cost_mask.sum()
            df.loc[negative_cost_mask, 'cost'] = abs(df.loc[negative_cost_mask, 'cost'])
            self.cleaning_stats['issues_found']['negative_cost'] = negative_count
            self.logger.warning(f"Исправлено {negative_count} отрицательных себестоимостей")
            fixes_count += negative_count
        
        invalid_discount_mask = (df['discount'] < 0) | (df['discount'] > 1)
        if invalid_discount_mask.any():
            invalid_count = invalid_discount_mask.sum()
            
            df.loc[df['discount'] < 0, 'discount'] = 0
            df.loc[df['discount'] > 1, 'discount'] = 1
            
            self.cleaning_stats['issues_found']['invalid_discount'] = invalid_count
            self.logger.warning(f"Исправлено {invalid_count} некорректных скидок")
            fixes_count += invalid_count
        
        self.cleaning_stats['fixed_values'] += fixes_count
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_len = len(df)
        df = df.drop_duplicates()
        removed = initial_len - len(df)
        
        if removed > 0:
            self.logger.info(f"Удалено {removed} дубликатов")
        
        return df
    
    def _remove_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        initial_len = len(df)
        
        invalid_mask = (
            (df['qty'] <= 0) |
            (df['price'] <= 0) |
            (df['cost'] <= 0) |
            (df['date'].isna())
        )
        
        if invalid_mask.any():
            invalid_count = invalid_mask.sum()
            df = df[~invalid_mask].copy()
            self.cleaning_stats['issues_found']['invalid_rows_removed'] = invalid_count
            self.logger.warning(f"Удалено {invalid_count} строк с некорректными данными")
        
        return df
    
    def get_cleaning_stats(self) -> dict:
        """Возвращает статистику очистки"""
        return self.cleaning_stats