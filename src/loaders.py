import pandas as pd
import logging
from pathlib import Path

def load_sales_data(filepath: str) -> pd.DataFrame:

    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Загрузка данных продаж из {filepath}")
        
        # Проверка существования файла
        if not Path(filepath).exists():
            error_msg = f"Файл не найден: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Загрузка данных
        df = pd.read_csv(filepath, encoding='utf-8-sig')
        
        # Проверка обязательных колонок
        required_columns = ['date', 'store_id', 'order_id', 'product_id', 
                           'product_name', 'category', 'qty', 'price', 
                           'discount', 'cost']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют обязательные колонки: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Успешно загружено {len(df)} строк продаж")
        return df
        
    except pd.errors.EmptyDataError:
        error_msg = f"Файл пуст: {filepath}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Ошибка при загрузке данных: {str(e)}"
        logger.error(error_msg)
        raise

def load_stores_data(filepath: str) -> pd.DataFrame:
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Загрузка данных магазинов из {filepath}")
        
        # Проверка существования файла
        if not Path(filepath).exists():
            error_msg = f"Файл не найден: {filepath}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Загрузка данных
        df = pd.read_csv(filepath)
        
        # Проверка обязательных колонок
        required_columns = ['store_id', 'city', 'format']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют обязательные колонки: {missing_columns}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Успешно загружено {len(df)} магазинов")
        return df
        
    except pd.errors.EmptyDataError:
        error_msg = f"Файл пуст: {filepath}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Ошибка при загрузке данных магазинов: {str(e)}"
        logger.error(error_msg)
        raise

def validate_data_quality(df: pd.DataFrame, df_name: str) -> dict:

    logger = logging.getLogger(__name__)
    
    stats = {
        'total_rows': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'columns': list(df.columns)
    }
    
    logger.info(f"Статистика данных {df_name}:")
    logger.info(f"  Всего строк: {stats['total_rows']}")
    logger.info(f"  Дубликаты: {stats['duplicate_rows']}")
    
    for col, missing in stats['missing_values'].items():
        if missing > 0:
            logger.warning(f"  Колонка '{col}': {missing} пропущенных значений ({missing/stats['total_rows']:.1%})")
    
    return stats