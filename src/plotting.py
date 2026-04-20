"""
Модуль для построения графиков и визуализации
"""
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import logging
from pathlib import Path
import os
import numpy as np

matplotlib.use('Agg')  # Для работы без GUI

class PlotGenerator:
    """Класс для генерации графиков"""
    
    def __init__(self, charts_dir: str = 'charts'):
        self.logger = logging.getLogger(__name__)
        self.charts_dir = charts_dir
        
        # Создаем папку для графиков если её нет
        os.makedirs(charts_dir, exist_ok=True)
        
        # Настройка стиля графиков
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def generate_all_charts(self, daily_metrics: pd.DataFrame, 
                          category_metrics: pd.DataFrame):

        self.logger.info("Генерация графиков")
        
        # График выручки по дням
        revenue_chart = self.plot_daily_revenue(daily_metrics)
        
        # График прибыли по дням
        profit_chart = self.plot_daily_profit(daily_metrics)
        
        # График топ категорий
        categories_chart = self.plot_top_categories(category_metrics)
        
        self.logger.info(f"Все графики сохранены в папку: {self.charts_dir}")
        
        return {
            'revenue': revenue_chart,
            'profit': profit_chart,
            'categories': categories_chart
        }
    
    def plot_daily_revenue(self, daily_metrics: pd.DataFrame):
        """Строит график выручки по дням"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Сортируем по дате
        df_sorted = daily_metrics.sort_values('date')
        
        # Линия выручки
        ax.plot(df_sorted['date'], df_sorted['total_revenue'], 
                linewidth=2.5, color='#2E86AB', marker='o', markersize=6,
                label='Выручка')
        
        # Заполнение под линией
        ax.fill_between(df_sorted['date'], df_sorted['total_revenue'], 
                       alpha=0.2, color='#2E86AB')
        
        # Настройка осей и заголовка
        ax.set_title('Динамика выручки по дням', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Выручка, руб.', fontsize=12)
        
        # Форматирование оси X (даты)
        fig.autofmt_xdate(rotation=45)
        
        # Сетка
        ax.grid(True, alpha=0.3)
        
        # Легенда
        ax.legend(loc='upper left')
        
        # Аннотация максимального значения
        max_revenue_idx = df_sorted['total_revenue'].idxmax()
        max_date = df_sorted.loc[max_revenue_idx, 'date']
        max_revenue = df_sorted.loc[max_revenue_idx, 'total_revenue']
        
        ax.annotate(f'Макс: {max_revenue:,.0f} руб.', 
                   xy=(max_date, max_revenue),
                   xytext=(max_date, max_revenue * 1.05),
                   arrowprops=dict(arrowstyle='->', color='red'),
                   fontsize=10, color='red')
        
        # Сохранение
        filepath = Path(self.charts_dir) / 'daily_revenue.png'
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"График выручки сохранён: {filepath}")
        return filepath
    
    def plot_daily_profit(self, daily_metrics: pd.DataFrame):
        """Строит график прибыли по дням"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Сортируем по дате
        df_sorted = daily_metrics.sort_values('date')
        
        # Линия прибыли
        ax.plot(df_sorted['date'], df_sorted['total_profit'], 
                linewidth=2.5, color='#A23B72', marker='s', markersize=6,
                label='Прибыль')
        
        # Заполнение под линией (только положительные значения)
        profit_positive = df_sorted['total_profit'].copy()
        profit_positive[profit_positive < 0] = 0
        ax.fill_between(df_sorted['date'], profit_positive, 
                       alpha=0.2, color='#A23B72')
        
        # Закрашивание отрицательных значений другим цветом
        profit_negative = df_sorted['total_profit'].copy()
        profit_negative[profit_negative > 0] = 0
        if (profit_negative < 0).any():
            ax.fill_between(df_sorted['date'], profit_negative, 
                           alpha=0.3, color='#FF6B6B')
        
        # Настройка осей и заголовка
        ax.set_title('Динамика прибыли по дням', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Прибыль, руб.', fontsize=12)
        
        # Горизонтальная линия на уровне 0
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        
        # Форматирование оси X
        fig.autofmt_xdate(rotation=45)
        
        # Сетка
        ax.grid(True, alpha=0.3)
        
        # Легенда
        ax.legend(loc='upper left')
        
        # Аннотация максимальной прибыли
        max_profit_idx = df_sorted['total_profit'].idxmax()
        max_date = df_sorted.loc[max_profit_idx, 'date']
        max_profit = df_sorted.loc[max_profit_idx, 'total_profit']
        
        ax.annotate(f'Макс прибыль: {max_profit:,.0f} руб.', 
                   xy=(max_date, max_profit),
                   xytext=(max_date, max_profit * 1.1),
                   arrowprops=dict(arrowstyle='->', color='green'),
                   fontsize=10, color='green')
        
        # Сохранение
        filepath = Path(self.charts_dir) / 'daily_profit.png'
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"График прибыли сохранён: {filepath}")
        return filepath
    
    def plot_top_categories(self, category_metrics: pd.DataFrame, top_n: int = 10):
        """Строит график топ категорий по выручке"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Берем топ-N категорий
        top_categories = category_metrics.head(top_n).copy()
        
        # 1. Bar chart - выручка по категориям
        bars = ax1.barh(top_categories['category'], top_categories['revenue'],
                       color=plt.cm.Set3(np.arange(len(top_categories)) / len(top_categories)))
        
        ax1.set_title(f'Топ-{top_n} категорий по выручке', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Выручка, руб.', fontsize=12)
        ax1.invert_yaxis()  # Самая большая сверху
        
        # Добавляем значения на столбцы
        for i, (bar, revenue) in enumerate(zip(bars, top_categories['revenue'])):
            width = bar.get_width()
            ax1.text(width * 1.01, bar.get_y() + bar.get_height()/2,
                    f'{revenue:,.0f} руб.', ha='left', va='center', fontsize=9)
        
        # 2. Pie chart - доли категорий
        # Для pie chart берем немного меньше категорий для читаемости
        pie_categories = category_metrics.head(min(8, len(category_metrics)))
        
        # Создаем красивую цветовую схему
        colors = plt.cm.Paired(np.arange(len(pie_categories)) / len(pie_categories))
        
        wedges, texts, autotexts = ax2.pie(pie_categories['revenue'], 
                                          labels=pie_categories['category'],
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90,
                                          pctdistance=0.85)
        
        ax2.set_title('Доли категорий в общей выручке', fontsize=14, fontweight='bold')
        
        # Настройка текста
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        # Добавляем круг в центре для donut chart эффекта
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax2.add_artist(centre_circle)
        
        # Общая статистика на графике
        total_revenue = category_metrics['revenue'].sum()
        top_n_share = top_categories['revenue'].sum() / total_revenue * 100
        
        fig.suptitle(f'Анализ категорий товаров\n'
                    f'Топ-{top_n} категорий дают {top_n_share:.1f}% выручки', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        plt.tight_layout()
        
        # Сохранение
        filepath = Path(self.charts_dir) / 'top_categories.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"График категорий сохранён: {filepath}")
        return filepath
    
    def create_dashboard(self, daily_metrics: pd.DataFrame, 
                        store_metrics: pd.DataFrame,
                        category_metrics: pd.DataFrame):
        """Создаёт дашборд с несколькими графиками на одном изображении"""
        try:
            fig = plt.figure(figsize=(18, 12))
            
            # 1. Выручка по дням (левый верхний)
            ax1 = plt.subplot(2, 2, 1)
            df_sorted = daily_metrics.sort_values('date')
            ax1.plot(df_sorted['date'], df_sorted['total_revenue'], 
                    color='#2E86AB', linewidth=2)
            ax1.fill_between(df_sorted['date'], df_sorted['total_revenue'], 
                            alpha=0.2, color='#2E86AB')
            ax1.set_title('Динамика выручки', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Дата')
            ax1.set_ylabel('Выручка, руб.')
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # 2. Прибыль по дням (правый верхний)
            ax2 = plt.subplot(2, 2, 2)
            ax2.plot(df_sorted['date'], df_sorted['total_profit'], 
                    color='#A23B72', linewidth=2)
            ax2.fill_between(df_sorted['date'], df_sorted['total_profit'], 
                            where=(df_sorted['total_profit'] > 0),
                            alpha=0.2, color='#A23B72')
            ax2.fill_between(df_sorted['date'], df_sorted['total_profit'], 
                            where=(df_sorted['total_profit'] < 0),
                            alpha=0.2, color='#FF6B6B')
            ax2.set_title('Динамика прибыли', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Дата')
            ax2.set_ylabel('Прибыль, руб.')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # 3. Топ категорий (левый нижний)
            ax3 = plt.subplot(2, 2, 3)
            top_cats = category_metrics.head(8)
            bars = ax3.barh(top_cats['category'], top_cats['revenue'],
                          color=plt.cm.Set3(range(len(top_cats))))
            ax3.set_title('Топ-8 категорий по выручке', fontsize=14, fontweight='bold')
            ax3.set_xlabel('Выручка, руб.')
            ax3.invert_yaxis()
            
            # 4. Топ магазинов (правый нижний)
            ax4 = plt.subplot(2, 2, 4)
            top_stores = store_metrics.head(6)
            bars = ax4.bar(range(len(top_stores)), top_stores['total_revenue'],
                         color=plt.cm.Pastel1(range(len(top_stores))))
            ax4.set_title('Топ-6 магазинов по выручке', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Магазин')
            ax4.set_ylabel('Выручка, руб.')
            ax4.set_xticks(range(len(top_stores)))
            ax4.set_xticklabels(top_stores['store_id'], rotation=45)
            
            # Общий заголовок
            total_revenue = daily_metrics['total_revenue'].sum()
            total_profit = daily_metrics['total_profit'].sum()
            fig.suptitle(f'Дашборд аналитики продаж\n'
                        f'Общая выручка: {total_revenue:,.0f} руб. | '
                        f'Общая прибыль: {total_profit:,.0f} руб.', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            plt.tight_layout()
            
            filepath = Path(self.charts_dir) / 'sales_dashboard.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Дашборд сохранён: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании дашборда: {str(e)}")
            return None