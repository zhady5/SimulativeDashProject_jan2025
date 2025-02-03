import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from preparation_data.functions import get_current_previous_sums


def create_fig_posts_inds(posts, selected_channel, date_range, bgcolor='#ffb347', word_color = '#666', contr_color = '#f5dfbf', graph_color='#F5DEB3', color_Nx_size='#8B4513'):
    if selected_channel is None:
        st.write({})  # Вывод пустой фигуры
        return


    subdf_channel = posts[posts.channel_name == selected_channel][['channel_name', 'date', 'cnt']].drop_duplicates()

    # Проверяем, что дата присутствует и не пуста
    if len(subdf_channel) == 0 or 'date' not in subdf_channel.columns or 'cnt' not in subdf_channel.columns:
        st.write({})
        return

    # Преобразуем строку в datetime
    #subdf_channel.loc[:, 'date'] = pd.to_datetime(subdf_channel['date'])
    start_time, end_time = date_range
    # Создаем полный диапазон дат между минимальными и максимальными значениями
    full_dates = pd.date_range(start=start_time, end=end_time, freq='D')
    
    # Присваиваем нулевые значения для отсутствующих дат
    new_df = pd.DataFrame({'date': full_dates, 'cnt': 0})
    new_df['date'] = pd.to_datetime(new_df['date'])


    subdf_posts = subdf_channel[(pd.to_datetime(subdf_channel['date']).dt.date >= start_time) & 
                                (pd.to_datetime(subdf_channel['date']).dt.date <= end_time)]
    # Используем pd.concat для объединения двух DataFrames
    merged_df = pd.concat([new_df, subdf_posts], ignore_index=True)
    
    # Удаляем дубликаты строк по дате и заполняем NaN значениями из других строк
    merged_df.drop_duplicates(subset='date', keep='first', inplace=True)
    merged_df.set_index('date', inplace=True)
    merged_df.fillna(0, inplace=True)
    merged_df.reset_index(inplace=True)
    merged_df.date = merged_df.date.astype(str)
         
    
    # Создание subplots
    fig_posts = make_subplots(
        rows=3,
        cols=2,
        column_widths=[0.85, 0.15],  # Ширина первой колонки 85%, второй — 15%
        specs=[
            [{"rowspan": 3}, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
        ],
        vertical_spacing=0.13
    )
    
    mean_cnt = subdf_posts.cnt.mean()
    colors = [color_Nx_size if val >= 2 * mean_cnt else graph_color for val in merged_df['cnt']]
    
    fig_posts.add_trace(go.Bar(x=merged_df.date, y=merged_df.cnt, marker_color=colors,
                               hovertemplate='%{x} <br>Публикаций: %{y}<extra></extra>'), row=1, col=1)
    
    period_names = dict({'days': 'вчера', 'weeks': 'неделю', 'months': 'месяц'})
    for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
        current, previous = get_current_previous_sums(merged_df, 'cnt', period)
        
        fig_posts.add_trace(
            go.Indicator(
                value=current,
                title={"text": f"<span style='font-size:0.65em;color:{word_color}'>Публикаций за {period_names[period[0]]}<br><span style='font-size:0.8em;color:gray'>Пред. знач.: {round(previous)}</span>"},
                mode="number+delta",
                number={'font': {'size': 32}},  # Задаем размер шрифта для текущего значения
                delta={'reference': previous, 'relative': True, "valueformat": ".2%", 'font': {'size': 28}},
            ), row=i + 1, col=2
        )
    
    # Настройка стиля графика
    fig_posts.update_layout(
        template="simple_white",
        font_family="Georgia",
        font_size=13,
        margin=dict(l=40, r=60, t=60, b=10),
        paper_bgcolor= bgcolor, #'#ffb347', #'rgba(0,0,0,0)',
        plot_bgcolor= bgcolor, #'rgba(0,0,0,0)',
        xaxis=dict(
            rangeselector=dict(  # Добавляем элементы управления диапазоном
                bgcolor=contr_color,  # Фоновый цвет области с кнопками
                font=dict(color="#333"),  # Цвет текста на кнопках
                activecolor=bgcolor,  # Цвет активной кнопки
                bordercolor=contr_color,  # Цвет рамки вокруг кнопок
                buttons=list([
                    dict(count=2, label="2д", step="day", stepmode="backward"),
                    dict(count=14, label="2н", step="day", stepmode="backward"),
                    dict(count=2, label="2м", step="month", stepmode="backward"),
                    dict(step="all")  # Кнопка для просмотра всего диапазона
                ])
            )
        )
    )
    return fig_posts
