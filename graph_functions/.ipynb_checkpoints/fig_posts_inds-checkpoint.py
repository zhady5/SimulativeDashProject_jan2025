import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from preparation_data.functions import get_current_previous_sums


def create_fig_posts_inds(posts, selected_channel, bgcolor='#ffb347', word_color = '#666', contr_color = '#f5dfbf', graph_color='#F5DEB3', color_Nx_size='#8B4513'):
    if selected_channel is None:
        st.write({})  # Вывод пустой фигуры
        return

    subdf_posts = posts[posts.channel_name == selected_channel][['channel_name', 'date', 'cnt']].drop_duplicates()

    # Проверяем, что дата присутствует и не пуста
    if len(subdf_posts) == 0 or 'date' not in subdf_posts.columns or 'cnt' not in subdf_posts.columns:
        st.write({})
        return
    
    
    # Создание subplots
    fig_posts = make_subplots(
        rows=3,
        cols=2,
        specs=[
            [{"rowspan": 3}, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
            [None, {'type': 'indicator'}],
        ],
        vertical_spacing=0.08
    )
    
    mean_cnt = subdf_posts.cnt.mean()
    colors = [color_Nx_size if val >= 2 * mean_cnt else graph_color for val in subdf_posts['cnt']]
    
    fig_posts.add_trace(go.Bar(x=subdf_posts.date, y=subdf_posts.cnt, marker_color=colors,
                               hovertemplate='%{x} <br>Публикаций: %{y}<extra></extra>'), row=1, col=1)
    
    period_names = dict({'days': 'вчера', 'weeks': 'неделю', 'months': 'месяц'})
    for i, period in enumerate([('days', 'days', 1), ('weeks', 'weeks', 1), ('months', 'months', 1)]):
        current, previous = get_current_previous_sums(subdf_posts, 'cnt', period)
        
        fig_posts.add_trace(
            go.Indicator(
                value=current,
                title={"text": f"<span style='font-size:0.8em;color:{word_color}'>Публикаций за {period_names[period[0]]}</span>"},
                mode="number+delta",
                delta={'reference': previous, 'relative': True, "valueformat": ".2%"},
            ), row=i + 1, col=2
        )
    
    # Настройка стиля графика
    fig_posts.update_layout(
        template="simple_white",
        font_family="Georgia",
        font_size=12,
        margin=dict(l=40, r=20, t=40, b=10),
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
