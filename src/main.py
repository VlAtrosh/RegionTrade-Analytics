import sys
import os
from pathlib import Path
import logging
from datetime import datetime

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем наши модули
from src.loaders import load_sales_data, load_stores_data, validate_data_quality
from src.cleaning import DataCleaner
from src.metrics import MetricsCalculator
from src.reporting import ReportGenerator
from src.plotting import PlotGenerator

def setup_logging():
    """Настраивает логирование"""
    # Создаем папку для логов если её нет
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Настройка формата логирования
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настройка файла логов
    log_file = log_dir / 'analysis.log'
    
    # Базовый конфиг
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("НАЧАЛО АНАЛИЗА ПРОДАЖ")
    logger.info("=" * 60)
    
    return logger

def main():
    """Основная функция запуска аналитики"""
    logger = setup_logging()
    
    try:
        # Пути к данным
        data_dir = Path('data')
        sales_file = data_dir / 'sales.csv'
        stores_file = data_dir / 'stores.csv'
        
        logger.info(f"Входные файлы:")
        logger.info(f"  Продажи: {sales_file}")
        logger.info(f"  Магазины: {stores_file}")
        
        # 1. Загрузка данных
        logger.info("\n1. ЗАГРУЗКА ДАННЫХ")
        sales_df = load_sales_data(str(sales_file))
        stores_df = load_stores_data(str(stores_file))
        
        # Валидация качества данных
        sales_stats = validate_data_quality(sales_df, 'sales')
        stores_stats = validate_data_quality(stores_df, 'stores')
        
        # 2. Очистка данных
        logger.info("\n2. ОЧИСТКА ДАННЫХ")
        cleaner = DataCleaner()
        cleaned_sales_df = cleaner.clean_sales_data(sales_df)
        
        # 3. Расчёт метрик
        logger.info("\n3. РАСЧЁТ МЕТРИК")
        calculator = MetricsCalculator()
        
        # Расчёт KPI для каждой строки
        sales_with_kpi = calculator.calculate_kpi(cleaned_sales_df)
        
        # Расчёт агрегированных метрик
        daily_metrics = calculator.calculate_daily_metrics(sales_with_kpi)
        store_metrics = calculator.calculate_store_metrics(sales_with_kpi, stores_df)
        top_products = calculator.calculate_top_products(sales_with_kpi)
        category_metrics = calculator.calculate_category_metrics(sales_with_kpi)
        
        # 4. Генерация отчётов
        logger.info("\n4. ГЕНЕРАЦИЯ ОТЧЁТОВ")
        reporter = ReportGenerator()
        reporter.generate_all_reports(
            sales_with_kpi, stores_df, daily_metrics, 
            store_metrics, top_products, category_metrics
        )
        
        # 5. Визуализация
        logger.info("\n5. ВИЗУАЛИЗАЦИЯ")
        plotter = PlotGenerator()
        charts = plotter.generate_all_charts(daily_metrics, category_metrics)
        
        # Дополнительный дашборд
        dashboard = plotter.create_dashboard(daily_metrics, store_metrics, category_metrics)
        if dashboard:
            logger.info(f"Дашборд сохранён: {dashboard}")
        
        # 6. Вывод сводки в консоль
        logger.info("\n6. ФИНАЛЬНАЯ СВОДКА")
        reporter.print_console_summary(daily_metrics, store_metrics, category_metrics)
        
        # 7. Логирование итогов
        logger.info("\n" + "=" * 60)
        logger.info("АНАЛИЗ УСПЕШНО ЗАВЕРШЁН")
        logger.info("=" * 60)
        
        cleaning_stats = cleaner.get_cleaning_stats()
        logger.info(f"ИТОГОВАЯ СТАТИСТИКА:")
        logger.info(f"  Загружено строк: {cleaning_stats['initial_rows']}")
        logger.info(f"  Обработано строк: {cleaning_stats['final_rows']}")
        logger.info(f"  Удалено строк: {cleaning_stats['removed_rows']}")
        logger.info(f"  Исправлено значений: {cleaning_stats['fixed_values']}")
        
        logger.info(f"\nСОЗДАННЫЕ ФАЙЛЫ:")
        logger.info(f"  Отчёты: output/")
        for file in Path('output').glob('*'):
            if file.is_file():
                logger.info(f"    - {file.name}")
        
        logger.info(f"  Графики: charts/")
        for file in Path('charts').glob('*.png'):
            logger.info(f"    - {file.name}")
        
        logger.info(f"\nВремя завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Файл не найден: {str(e)}")
        logger.error("Проверьте наличие файлов sales.csv и stores.csv в папке data/")
        logger.error("Или запустите generate_test_data.py для создания тестовых данных")
        return 1
        
    except Exception as e:
        logger.error(f"Критическая ошибка при выполнении: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)