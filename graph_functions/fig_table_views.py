import streamlit as st
import pandas as pd
from datetime import datetime
import math


def table_views(table_day_views, max_days, channel):
    text_cols = 6
    sub_tab_final = table_day_views[table_day_views.channel_name==channel].iloc[:, 1:text_cols+max_days]
    sub_tab_final.columns = ["ID поста", "Текст поста", "Ссылка", "Дата публикации", "Текущие просмотры"] + [f"{i} д" for i in range(1, max_days+1)]


    return sub_tab_final.drop_duplicates()


def styled_df(df, dark_color = '#8B0000', clr='#006a4e'):
    def contains_substring(string, substring):
        # Если подстрока найдена в исходной строке, возвращаем True
        if substring in string:
            return True
        # В противном случае возвращаем False
        else:
            return False

    # Определение списков ключевых слов для разных уровней значимости
    keywords_top = ['(100', '(9', '(8']
    keywords_median = ['(7', '(6', '(5', '(4', '(3']
    keywords_bottom = ['(2', '(1']
    
    def style_contains(cell_value):
        # Проверяем, является ли значение строки и содержит ли оно ключевое слово из списка top
        if isinstance(cell_value, str) and any(keyword in cell_value for keyword in keywords_top) \
                and len(cell_value.split(' (')[1].split('.')[0]) > 1:
            return 'color: #008000'
        
        # Аналогично проверяем для медианных значений
        elif isinstance(cell_value, str) and any(keyword in cell_value for keyword in keywords_median) \
                and len(cell_value.split(' (')[1].split('.')[0]) > 1:
            return 'color: #006994'
        
        # И наконец, для bottom значений
        elif isinstance(cell_value, str) and any(keyword in cell_value for keyword in keywords_bottom) \
                and len(cell_value.split(' (')[1].split('.')[0]) > 1:
            return 'color: #006994'
            
        # Специальный случай для одиночных символов после скобки
        elif isinstance(cell_value, str) and contains_substring(cell_value, ' (') \
                 and len(cell_value.split(' (')[1].split('.')[0]) == 1 and cell_value.split(' (')[1].split('.')[0] != '0':
            return 'color: #fd0e35'        
        # Специальный случай для одиночных символов после скобки
        elif isinstance(cell_value, str) and contains_substring(cell_value, ' (') \
                 and len(cell_value.split(' (')[1].split('.')[0]) == 1 and cell_value.split(' (')[1].split('.')[0] == '0':
            return 'color: #333'
        
        # Для всех остальных случаев оставляем стиль по умолчанию
        else:
            return ''
     # Создаем мини-гистограммы для колонки "Текущие просмотры"
    def add_bar(s):
        n = s.name
        if n == "Текущие просмотры":
            # Используем генератор списков для выполнения деления для каждого элемента
            return [
            f'background: linear-gradient(to right, {clr} 0%, {clr} {(v / s.max()) * 100}%, transparent {(v / s.max()) * 100}%, transparent 100%);'
            for v in s
        ]
        return [''] * len(s)
    # Применение функции стилей ко всем ячейкам DataFrame
    styled_df = df.style.map(style_contains).apply(add_bar, axis=0)
    
      # Установка стиля для заголовков
    styled_df.set_table_styles([
        {'selector': 'th', 'props': [('color', dark_color)]},
         {'selector': 'tr', 'props': [('border-bottom', '0.5px solid gray')]},
    ])
    
    # Изменение размера шрифта для всей таблицы
    styled_df.set_properties(**{'font-size': '10pt'})
    return styled_df
