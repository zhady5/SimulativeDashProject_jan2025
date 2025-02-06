import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from preparation_data.functions import get_current_previous_sums


def create_fig_subs_inds(subs, selected_channel, date_range, bgcolor='#ffb347', word_color = '#666', contr_color='#f5dfbf', graph_color='#F5DEB3'):
    if selected_channel is None:
        st.write({})  # Вывод пустой фигуры
        return

    subdf_channel = subs[subs.channel_name == selected_channel][['channel_name', 'date', 'subs_cnt', 'subs_change']].drop_duplicates()

    # Проверяем, что дата присутствует и не пуста
    if len(subdf_channel) == 0 or 'date' not in subdf_channel.columns or 'subs_cnt' not in subdf_channel.columns:
        st.write({})
        return

    # Преобразуем строку в datetime
    #subdf_channel.loc[:, 'date'] = pd.to_datetime(subdf_channel['date'])
    start_time, end_time = date_range

    subdf_subs = subdf_channel[(pd.to_datetime(subdf_channel['date']).dt.date >= start_time) & 
                                (pd.to_datetime(subdf_channel['date']).dt.date <= end_time)]

    
    # График по подписчикам
    
    # Создание subplots
    fig_subs = make_subplots(
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
    
    mean_subs = subdf_subs.subs_cnt.mean()
    #colors = ['#8B4513' if val >= 2 * mean_subs else '#F5DEB3' for val in subdf_subs['subs_cnt']]
    
    #fig_subs.add_trace(go.Bar(x=subdf_subs.date, y=subdf_subs.subs_cnt, marker_color=colors,
    #                          hovertemplate='%{x} <br>Подписчиков: %{y}<extra></extra>'), row=1, col=1)

        # Добавляем след для заполнения области
    fig_subs.add_trace(go.Scatter(
        x=subdf_subs.datetime,
        y=subdf_subs.subs_cnt,
        fill='tozeroy',
        fillcolor = contr_color,
        mode='none',  # Без маркеров или линий
        hoverinfo='skip',  # Отключаем hover для этого следа
    ), row=1, col=1)

    
    fig_subs.add_trace(go.Scatter(
                    x=subdf_subs.datetime, 
                    y=subdf_subs.subs_cnt, 
                    mode='markers',  # Изменено с 'lines+markers' на 'markers'
                    marker=dict(
                    color=graph_color,
                    size=8,  # Увеличен размер маркера для лучшей видимости
                    line=dict(
                        color=contr_color,
                        width=1
                    )
                ),
                hovertemplate='%{x} <br>Подписчиков: %{y}<extra></extra>'
            ), row=1, col=1)
    
    period_names = dict({'days': 'вчера', 'weeks': 'неделю', 'months': 'месяц'})
    for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
        current, previous = get_current_previous_sums(subdf_subs, 'subs_change', period)
        
        fig_subs.add_trace(
            go.Indicator(
                value=current,
                title={"text": f"<span style='font-size:0.8em;color:{word_color}'>Подписчиков за {period_names[period[0]]}<br><span style='font-size:0.8em;color:gray'>Пред. знач.: {round(previous)}</span>"},
                mode="number+delta",
                delta={'reference': previous, 'relative': True, "valueformat": ".2%"},
            ), row=i + 1, col=2
        )

    # устанавливаем нижнюю границу диапазона в 0, а верхнюю - на 10% выше максимального значения
    fig_subs.update_yaxes(range=[0, max(subdf_subs.subs_cnt) * 1.1], row=1, col=1)

    # Обновляем макет, чтобы убрать легенду (так как у нас два следа для одних данных)
    fig_subs.update_layout(showlegend=False)
    
    # Настройка стиля графика
    fig_subs.update_layout(
        template="simple_white",
        font_family="Georgia",
        font_size=13,
        margin=dict(l=40, r=60, t=60, b=10),
        paper_bgcolor= bgcolor, #'rgba(0,0,0,0)',
        plot_bgcolor= bgcolor, #'rgba(0,0,0,0)',
        xaxis=dict(
            rangeselector=dict(  # Добавляем элементы управления диапазоном
                bgcolor=contr_color,  # Фоновый цвет области с кнопками
                font=dict(color=word_color),  # Цвет текста на кнопках
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
    return fig_subs
