import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
#from functions import get_current_previous_sums, date_ago
import datetime
import colorlover as cl


def create_bubble_fig(filtered_df, bgcolor = '#ffb347', word_color = '#666', colors = cl.scales['9']['seq']['OrRd'][::-1] ):
        # Проверяем, что дата присутствует и не пуста
        if len(filtered_df) == 0:
            st.write('нет данных')
            return
        else:
                gr_pvr_sum = filtered_df.drop(['reaction_type', 'react_cnt'], axis=1).drop_duplicates()
            
                if gr_pvr_sum.shape[0] == 0:
                    st.write('недостаточно нужных полей')
                    return
        
        # Создаем градиент 
        #colors = cl.scales['9']['seq']['OrRd'][::-1] 
        
    # Предположим, что у тебя уже есть DataFrame под названием gr_pvr_sum
                fig = go.Figure()
                
                # Добавление точек на график
                fig.add_trace(go.Scatter(
                    x=gr_pvr_sum['current_views'],
                    y=gr_pvr_sum['idx_active'],
                    mode='markers',
                    marker=dict(
                        size=gr_pvr_sum['text_len'],
                        color=gr_pvr_sum['current_views'],   
                        colorscale=colors,
                        showscale=False,  # Скрывает colorbar
                        sizemode='area',
                        sizeref=2. * max(0, max(gr_pvr_sum['text_len'])) / (18.**2),
                        sizemin=4
                    ),
                    text=gr_pvr_sum[['post_id']],  # Показывает post_id и дату при наведении
                    hoverinfo='text+x+y+z',  # Настройка информации во всплывающей подсказке
                    hovertemplate=
                        '<b>ID Поста:</b> %{text}<br>' +
                        '<b>Текущие Просмотры:</b> %{x}<br>' +
                        '<b>Количество знаков в тексте:</b> %{marker.size}<br>' +  # Добавлен размер пузыря
                        '<b>Активность:</b> %{y} %<extra></extra>'
                ))
                
                # Логарифмическая ось X
                fig.update_xaxes(type="log")
            
            
                # Скрыть colorbar
                fig.update_layout(coloraxis_showscale=False)
            
                fig.update_layout(    
                    yaxis_title="Индекс активности, %",
                    xaxis_title="Текущее количество просмотров",         
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor= word_color,
                        tickfont_color = word_color,
                        showticklabels=True,
                        #dtick=10,
                        ticks='outside',
                        tickcolor = word_color,
                    ),
                    margin=dict(l=40, r=60, t=10, b=10),
                    showlegend=False,
                    paper_bgcolor = bgcolor,
                    plot_bgcolor = bgcolor,
                    hovermode='closest',
                )
                return fig    
