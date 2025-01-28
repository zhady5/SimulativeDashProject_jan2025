import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
#from functions import get_current_previous_sums, date_ago
import datetime

def create_heatmap(filtered_df, bgcolor = '#ffb347',  word_color = "#212121", min_color_heatmap = '#F5DEB3', max_color_heatmap = "#006a4e"):
    # Проверяем, что дата присутствует и не пуста
    if len(filtered_df) == 0:
        st.write({})
        return
    
    # Генерация данных
    filtered_df = filtered_df[['date', 'hour', 'cnt']].rename(columns={'cnt': 'publications'}).sort_values('date')
    raw_index = filtered_df.set_index(['date', 'hour'])

    # Проверяем, что дата присутствует и не пуста
    if len(filtered_df) == 0:
        st.write({})
        return
    
    dates = pd.to_datetime(filtered_df.date).unique().tolist()
    index = pd.MultiIndex.from_product([filtered_df.date.unique(), range(1, 25)], names=['date', 'hour'])
    raw = pd.DataFrame(index=index)
    df = raw.merge(raw_index, left_index=True, right_index=True, how='left')
    df.fillna(0, inplace=True)
    df = df.reset_index().drop_duplicates(subset=['date', 'hour']).set_index(['date', 'hour'])
    
    # Преобразование данных в формат, подходящий для heatmap
    z_values = df['publications'].unstack(level=-1)
    x_labels = [str(hour) for hour in range(1, 25)]
    y_labels = [date.strftime('%Y-%m-%d') for date in dates]

    
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=pd.DataFrame([[1] * len(x_labels)] * len(y_labels), columns=range(1, 25), index=y_labels),
                x=x_labels,
                y=y_labels,
                colorscale=[[0, bgcolor], [1, bgcolor]],
                showscale=False,
                hovertemplate='%{y} <br>%{x} ч <br>Публикаций: %{z}<extra></extra>'
            ),
            go.Heatmap(
                z=z_values,
                x=x_labels,
                y=y_labels,
                colorscale= [[0,  min_color_heatmap], [0.0000000001, max_color_heatmap], [1, max_color_heatmap]], #[[0, '#F5DEB3'], [1, '#8B0000' ]],
                showscale=False,
                xgap=10,
                ygap=10,
                hovertemplate='%{y} <br>%{x} ч <br>Публикаций: %{z}<extra></extra>'
            )
        ]
    ).update_layout(
        font_family='Arial',
        margin=dict(l=30, r=50, t=0, b=20),
        paper_bgcolor=bgcolor,
        plot_bgcolor=bgcolor,
        legend_title_font_color=word_color,
        legend_font_color=word_color,
        legend_borderwidth=0,
        hoverlabel_font_family='Arial',
        hoverlabel_font_size=12,
        hoverlabel_font_color=word_color,
        hoverlabel_align='auto',
        hoverlabel_namelength=-1,
        hoverlabel_bgcolor='#FAFAFA',
        hoverlabel_bordercolor='#E5E4E2'
    )
    
    # Ограничиваем количество меток на оси Y до 10
    if len(y_labels) > 10:
        y_labels_subset = y_labels[::max(len(y_labels) // 10, 1)]
    else:
        y_labels_subset = y_labels
    
    # Перемещение подписей часов наверх
    fig.update_xaxes(side="top", tickfont=dict(family='Arial', size=8), dtick=1) # title_font=dict(family='Arial', size=10)
    
    fig.update_yaxes(
        #autorange="reversed",
        #dtick=max(len(y_labels) // 10, 1),
        #ticktext=y_labels,
        #tickvals=[datetime.datetime.strptime(date, "%Y-%m-%d").timestamp() for date in y_labels_subset],
        #tickformat="%b %d, %y",
        tickfont={"family": "Arial", "size": 8},
        title_font={"family": "Arial", "size": 14}
    )
    
    # Добавляем полосу прокрутки для оси Y
    fig.update_layout(
        font_size=9,
        yaxis_title="Дата",
        xaxis_title="Часы",
        yaxis=dict(autorange="reversed"),  # tickangle=45,  # Наклон меток для улучшения читаемости
        
    )

    return fig
