import streamlit as st
import os
import math
from numbers import Number
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
    
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

from plottable import ColumnDefinition, Table
from plottable.cmap import normed_cmap
#from plottable.formatters import decimal_to_percent
from plottable.plots import circled_image # image

figsize = (28,35)
header_size = 28
subheader_size = 22
text_size = 16
text_idx_size = 19
text_value_size = 19
font_size = 13

id1, val1 = 'ID поста (1)' , 'Текущее количество просмотров 👀'
id2, val2 = 'ID поста (2)' , 'Общее количество реакций 👍'
id3, val3 = 'ID поста (3)' , 'Индекс вовлеченности ❤️'
id4, val4 = 'ID поста (4)' , 'Подписались \Отписались 🏃‍♀️'

def create_table_top5(channels, posts, post_view, subs, gr_pvr,  channel, bgcolor='#FFA500', word_color='#666', cmap_colors = matplotlib.cm.autumn):
    # Проверяем, что дата присутствует и не пуста
    if channel is None  or len(posts) == 0 or len(subs) == 0 or len(gr_pvr) == 0:
        st.write({})
        return

    
    posts_link = posts[['id', 'text', 'channel_id']].merge(channels[['id', 'username']].rename(
                                                                                        columns={'id':'channel_id'}), on = 'channel_id').copy()
    posts_link.loc[:, 'text_short'] = posts_link.text.str[:10]
    posts_link.loc[:, 'link'] = 'https://t.me/' +  posts_link.username + '/'+ posts_link.id.astype(str)
    posts_link.drop(['text', 'username'], axis=1, inplace=True)
    
    
    def df_cnt_sub_between_posts(posts, subs, channel):
        p = posts[['id', 'datetime', 'channel_name' 
                      ]][posts.channel_name == channel].sort_values(by='datetime').copy()
        p = p.merge(posts_link, on = 'id').rename(columns={'id': 'post_id'})
        p['datetime'] = p['datetime'].apply(lambda d: pd.Timestamp(d))
        s = subs[['id', 'datetime', 'subs_cnt', 'channel_name','subs_change', 'subs_change_pos', 'subs_change_neg'
                                                                 ]][subs.channel_name == channel].sort_values(by='datetime').copy()
        s['datetime'] = s['datetime'].apply(lambda d: pd.Timestamp(d))

        p['datetime'] = pd.to_datetime(p['datetime'], errors='coerce')
        s['datetime'] = pd.to_datetime(s['datetime'], errors='coerce')
        
        df = pd.merge_asof(s, p, on='datetime', by = 'channel_name')
    
        return df.groupby(['channel_name', 'post_id',  'text_short', 'link'])[['subs_change', 'subs_change_pos', 'subs_change_neg']].sum().reset_index()
    
    def get_top(df, col, n=5):
        top5_views = df.nlargest(n, col)[['post_id',  'text_short', 'link', col]]
        
        # Исключаем строки с NaN перед конкатенацией
        top5_views = top5_views.dropna(how='all')
        
        return top5_views.reset_index(drop=True)
    
    
    def get_bottom(df, col, n=5):
        bottom5_views = df.nsmallest(n, col)[['post_id',  'text_short', 'link', col]].sort_values(by = col, ascending=False)
        
        # Исключаем строки с NaN перед конкатенацией
        bottom5_views = bottom5_views.dropna(how='all')
        
        return bottom5_views.reset_index(drop=True)
    
    def create_rows5(df, func,  post_subs_changes, col_change, nlargest=1):
        def rename_columns(data, num, col):
            data[f'post_id ({num})'] = data['post_id'].astype(str) + ' (' + data['text_short'] + ')'
            data.drop(['text_short', 'post_id'], axis=1, inplace=True)
            data.rename(columns={'link': f'link ({num})'}, inplace=True)
            return data[[f'post_id ({num})', f'link ({num})', f'{col}']]
        
        data_views = func(df, 'current_views', 5)
        data_react_sum = func(df, 'react_cnt_sum', 5)
        data_idx_active = func(df, 'idx_active', 5)
        if nlargest==1:
            data_post_subs = post_subs_changes[post_subs_changes[col_change]!=0].nlargest(5, col_change)[['post_id','text_short', 'link', col_change]]\
                                                                    .rename(columns={col_change: 'subs_change'})\
                                                                    .reset_index(drop=True)
        else:
            data_post_subs = post_subs_changes[post_subs_changes[col_change]!=0].nsmallest(5, col_change)[['post_id','text_short', 'link', col_change]]\
                                                                    .rename(columns={col_change: 'subs_change'})\
                                                                    .reset_index(drop=True)
        
        df = pd.concat([rename_columns(data_views, 1, 'current_views')
                        ,  rename_columns(data_react_sum, 2, 'react_cnt_sum')
                        ,  rename_columns(data_idx_active,3, 'idx_active')
                        , rename_columns(data_post_subs, 4, 'subs_change')
                       ], axis=1)
        
        

        
        df.columns = [f'{id1}', 'link (1)', f'{val1}', f'{id2}', 'link (2)', f'{val2}', f'{id3}', 'link (3)', f'{val3}', f'{id4}', 'link (4)', f'{val4}' ]
    
        return df
    
    def correct_data(df):
        df = df.set_index('ID поста (1)')   
    
        df = df.fillna('')
    
        #def is_number(obj):
        #    return isinstance(obj, Number)
            
        #df['ID поста (4)'] = df['ID поста (4)'].apply(lambda c: str(c).split('.')[0] if is_number(c) else c)
        #df['Текущее количество'] = df['Текущее количество'].astype(int)
    
        return df

    post_subs_changes = df_cnt_sub_between_posts(posts, subs, channel)
    gr_pvr = gr_pvr.merge(posts_link.rename(columns={'id':'post_id'}), on = 'post_id')
    df_cols = ['channel_name', 'post_id','post_datetime', 'text_short', 'link', 'current_views', 
             'react_cnt_sum', 'idx_active']
    df = gr_pvr[df_cols][gr_pvr.channel_name == channel].sort_values(by='current_views', ascending=False).drop_duplicates()

    if df.shape[0]==0:
        df_cols_pw = ['channel_name', 'post_id','post_datetime', 'current_views']
        df = post_view[df_cols_pw][post_view.channel_name == channel].sort_values(by='current_views', ascending=False).drop_duplicates()
        df = pd.concat([pd.DataFrame(columns=df_cols), df], axis=0)
        for c in ['current_views', 'react_cnt_sum', 'idx_active']:
            df[c] = df[c].astype(float)
    
    top5 = create_rows5(df, get_top, post_subs_changes, 'subs_change_pos')
    bottom5 = create_rows5(df, get_bottom, post_subs_changes, 'subs_change_neg', 0)
    
    df = pd.concat([top5, bottom5], axis=0)
    
    #cmap_colors =  matplotlib.cm.autumn  #matplotlib.cm.get_cmap('afmhot').reversed()
    
    cmap = LinearSegmentedColormap.from_list(
        name="lavender_to_midnight", colors= ['#FFFFFF', '#E6E6FA', '#9370DB', '#4B0082', '#191970'], N=256
    )   
    #["#ffffff", "#f2fbd2", "#c9ecb4", "#93d3ab", "#35b0ab"]
    
    basic_services_cols = [ f'{val1}', f'{val2}',  f'{val3}',  f'{val4}' ]
    
    df_final = df.copy()

#    col_defs = (
#        [
#            ColumnDefinition(
#                name="ID поста (1)",
#                textprops={"ha": "center", "weight": "bold", "fontsize":text_idx_size},
#                width=0.6,
#                group="Просмотры",
#            ),
#              ColumnDefinition(
#                name="Текущее количество",
#                width=0.65,
#                textprops={
#                    "ha": "center",
#                    "bbox": {"boxstyle": "circle", "pad": 0.95},
#                    "fontsize": text_value_size
#                },
#                cmap=normed_cmap(df["Текущее количество"], cmap=cmap_colors, num_stds=1), #matplotlib.cm.plasma
#                group="Просмотры",
#    
#            ),
#    
#            ColumnDefinition(
#                name="ID поста (2)",
#                textprops={"ha": "right", "weight": "bold", "fontsize": text_idx_size },
#                width=0.6,
#                group="Реакции",
#            ),
#                 ColumnDefinition(
#                name="Общее количество",
#                width=0.65,
#                textprops={
#                    "ha": "center",
#                    "bbox": {"boxstyle": "circle", "pad": 0.65},
#                    "fontsize":text_value_size
#                },
#                cmap=normed_cmap(df["Общее количество"], cmap=cmap_colors, num_stds=1),
#                group="Реакции",
#            ),
#    
#            ColumnDefinition(
#                name="ID поста (3)",
#                textprops={"ha": "right", "weight": "bold", "fontsize": text_idx_size },
#                width=0.6,
#                group="Вовлеченность",
#            ),
#              ColumnDefinition(
#                name="Индекс",
#                width=0.65,
#                textprops={
#                    "ha": "center",
#                    "bbox": {"boxstyle": "circle", "pad": 0.55},
#                    "fontsize": text_value_size
#                },
#                cmap=normed_cmap(df["Индекс"], cmap=cmap_colors, num_stds=1),
#                group="Вовлеченность",
#            ),
#    
#                    ColumnDefinition(
#                name="ID поста (4)",
#                textprops={"ha": "right", "weight": "bold", "fontsize": text_idx_size },
#                width=0.6,
#                group="Подписчики после публикации поста",
#            ),
#              ColumnDefinition(
#                name="Подписались\Отписались",
#                width=0.65,
#                textprops={
#                    "ha": "center",
#                    "bbox": {"boxstyle": "circle", "pad": 0.55},
#                    "fontsize":text_value_size - 5
#                },
#                cmap=normed_cmap(df["Подписались\Отписались"], cmap=cmap_colors, num_stds=1),
#                group="Подписчики после публикации поста",
#            ),
#            
#        ])
#    
#    plt.rcParams["font.family"] = ["DejaVu Sans"]
#    plt.rcParams["savefig.bbox"] = "tight"
#    
#    df_final = correct_data(df)
#    
#    fig, ax = plt.subplots(figsize=figsize) #
#    
#    # Set the figure and axes background to orange
#    fig.patch.set_facecolor(bgcolor) ##f5dfbf #'#FFA500'
#    ax.set_facecolor(bgcolor)
#    
#    table = Table(
#        df_final,
#        column_definitions=col_defs,
#        row_dividers=True,
#        footer_divider=True,
#        ax=ax,
#        textprops={"fontsize": text_size, 'color': word_color},
#        row_divider_kw={"linewidth": 1, "linestyle": (0, (1, 5))},
#        col_label_divider_kw={"linewidth": 1, "linestyle": "-"},
#        column_border_kw={"linewidth": 1, "linestyle": "-"},
#    )
#        
#    # Adding the bold header as a text annotation
#    header_text = "\n Лидеры и аутсайдеры среди постов"
#    header_props = {'fontsize': header_size, 'fontweight': 'bold', 'va': 'center', 'ha': 'center', 'color': word_color}
#    # Adjusting the y-coordinate to bring the header closer to the table
#    plt.text(0.5, 0.91, header_text, transform=fig.transFigure, **header_props)
#    
#    # Adding the subtitle at the top in gray
#    subtitle_text = "\n Таблица включает топ-5 постов с лучшими и худшими показателями по просмотрам, реакциям, индексу вовлеченности (Реакции/Просмотры) и динамике подписок. \n Анализ поможет понять, какой контент привлекает больше внимания, вызывает активность и влияет на рост аудитории. "
#    subtitle_props = {'fontsize': subheader_size, 'va': 'center', 'ha': 'center', 'color': word_color}
#    plt.text(0.5, 0.89, subtitle_text, transform=fig.transFigure, **subtitle_props)
#    
#    # Adding the footer text
#    #footer_text = "Источник: Данные Telegram API \n Обработка данных и дашборд - Альмира (@a1m_ra), Парсинг данных - Вероника (@chacter) "
#    #footer_props = {'fontsize': 14, 'va': 'center', 'ha': 'center', 'color': word_color}
#    # Adjusting the y-coordinate to position the footer closer to the bottom of the figure
#    #plt.text(0.5, 0.09, footer_text, transform=fig.transFigure, **footer_props)
#    
#    fig.savefig("tableTopBottom.png", facecolor=ax.get_facecolor(), dpi=200)
#
#    return fig
    
    # Generate HTML table with gradient circles around numbers
    html = "<style>table {width: 100%; border-collapse: collapse;} th, td {padding: 8px;text-align: center;border: 1px solid black;color: #666; font-size: 12px;} .circle {display: inline-block;border-radius: 50%;text-align: center;}</style>"
    html += f"<table><tr><th>ID поста (1)</th><th>{val1}</th><th>ID поста (2)</th><th>{val2}</th><th>ID поста (3)</th><th>{val3}</th><th>ID поста (4)</th><th>{val4}</th></tr>"
    
    # Calculate global min and max for each column
    global_min_max = {}
    for col in basic_services_cols:
        if df_final[col].dtype in [np.float64, np.int64]:
            global_min_max[col] = (df_final[col].min(), df_final[col].max())
            
    html += "<tr><td colspan='8' class='separator'></td></tr>"
    for index, row in df_final.iterrows():
        html += "<tr>"
        
        # Process all columns in order
        for i, col in enumerate(df_final.columns):
            value = row[col]
            if "ID поста" in col:
                link_col = f"link ({i//3 + 1})"  # Calculate corresponding link column
                link = row[link_col]
                if pd.notna(value) and pd.notna(link):  # Check that both values are not NaN
                    html += f"<td style='font-size: {font_size}px;' ><a href='{link}' target='_blank'>{value}</a></td>"
                else:
                    html += f"<td style='font-size: {font_size}px;' >{value}</td>"  # If no link, just show the ID
            elif isinstance(value, (int, float)) and not np.isnan(value) and col in basic_services_cols:
                if df_final[col].dtype in [np.float64, np.int64]:
                    min_val, max_val = global_min_max[col]
                    if min_val != max_val:
                        normalized_value = (value - min_val) / (max_val - min_val)
                    else:
                        normalized_value = 0
                        
                    circle_size = int(30 + normalized_value * 30)
                    circle_color = plt.cm.autumn(normalized_value)[:3]
                    if col != val3:
                        value = int(value)
                    circle_color_hex = "#{:02x}{:02x}{:02x}".format(int(circle_color[0]*255), int(circle_color[1]*255), int(circle_color[2]*255))
                    html += f"<td><div class='circle' style='width: {circle_size}px;height: {circle_size}px;line-height: {circle_size}px;background-color: {circle_color_hex};color: #333; font-size: {font_size}px;'>{value}</div></td>"
                else:
                    html +=  f"<td style='font-size: {font_size}px; color: #333'>{value}</td>" #f"<td>{value}</td>"
            else:
                if 'link' not in col:
                    html +=  f"<td style='font-size: {font_size}px; color: #333'>{value}</td>" #f"<td>{value}</td>"
    
        html += "</tr>"
        # Add separator row after the 5th row
        if index == 4:
            html += "<tr><td colspan='8' class='separator'></td></tr>"
    
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)
