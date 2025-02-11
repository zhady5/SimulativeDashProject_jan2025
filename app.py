import pandas as pd
import streamlit as st
from datetime import date
import colorlover as cl
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from preparation_data.data_processing import load_data, process_data
from preparation_data.functions import date_ago, create_slider
from graph_functions.metrics import calculate_mean_max_subs, calculate_mean_posts, calculate_mean_views, calculate_mean_reacts
from graph_functions.fig_posts_inds import create_fig_posts_inds
from graph_functions.fig_subs_inds import create_fig_subs_inds
from graph_functions.fig_heatmap import create_heatmap
from graph_functions.fig_subs_pos_neg import create_subs_pos_neg #, create_slider
from graph_functions.fig_bubble import create_bubble_fig
from graph_functions.fig_table_views import table_views, styled_df
from graph_functions.fig_image import make_image, prepare_data
from graph_functions.fig_table_top5 import create_table_top5


bgcolor =  'white' #'#f5a83d' #'#ff9600' #'#ffb347' # фон дашборда и графиков
contr_color = '#f5dfbf' #более светлый цвет для всех графиков и обводок кнопок
subheader_color = '#666'
word_color = '#333' #'#666' цвет шрифтов для всех текстов
min_color_heatmap = '#f2f3f4' #'#dcdcdc' # цвет для матрицы

metrics_number_color = 'brown' # цвет цифр у метрик
graph_color= '#f5a83d' #'#F5DEB3' # светлый цвет для всех графиокв и таблиц
color_Nx_size='#8B4513' # цвет для выделения N-кратного значения в графике с постами
dark_color = '#8B0000' # цвет для отписавшихся подписчиков и для заголовков в таблице с просмотрами по дням
max_color_heatmap = "#006a4e" # цвет для наличия постов в матрице для графика публикаций
cmap_colors = matplotlib.cm.Wistia #matplotlib.cm.autumn # градиент для топ5 постов по разным параметрам
colors_gradient_bubble = cl.scales['9']['seq']['OrRd'][::-1] # Создаем градиент для пузырькового графика

slider_months_ago = 1 # сколько месяцев назад для стартовой точки слайдера

#для примера другие градиенты
#cl.scales['9']['seq']['YlGnBu']: Палитра с переходами от желтого через зеленый и синий до темно-синего.
#cl.scales['9']['seq']['Blues']: Только синие оттенки, начиная со светло-голубого и заканчивая темным синим.
#cl.scales['9']['seq']['Reds']: Красные оттенки, начинающиеся с розового и заканчивающиеся насыщенным красным.
#cl.scales['9']['seq']['PuBu']: Переходы от пурпурного к голубому.
#cl.scales['9']['seq']['Greys']: Оттенки серого, от белого до черного.


palette_num = 21 # в файле 172 палетки для раскрашивания слов в облаке слов



st.set_page_config(layout="wide", page_icon="📊",)
# Стили заголовков и подзаголовков
st.markdown(f"""
<style>
    .title h1 {{
        font-family: 'Open Sans', sans-serif;
        font-size: 52px;
        line-height: 36px;
        color: {graph_color};
        background-color: {bgcolor};
        padding: 0px;
        box-shadow: 0 10px 15px rgba(0,0,0,0.05);
        border-radius: 10px;
        text-align: left;
    }}
    .subheader h2 {{
        font-family: 'Open Sans', sans-serif;
        font-size: 20px;
        background-color: {bgcolor};
        line-height: 24px;
        color: {subheader_color};
        margin-top: 0px;
        margin-bottom: 0px;
        font-weight: bold;
    }}

    .custom-text {{ color: {word_color}; 
                   font-size: 14px; 
                   }} 
    .custom-number {{ color: {metrics_number_color}; 
                     font-weight: bold; 
                     font-size: 16px; }}
    

    .button-container {{
        display: flex;
        justify-content: flex-start;
        gap: 0px;
        margin-bottom: 0px;
    }}
    .stButton > button {{
        background-color: {bgcolor};
        border-color: {contr_color};
        color: {word_color};
        border: 2px solid {contr_color};
        border-radius: 30px; 
        padding: 0px 8px;
        font-size: 16px;
        font-weight: 200;
        white-space: nowrap; 
        font-family: 'Roboto', sans-serif;
    }}
    .stButton > button:hover {{
        background-color: {contr_color};
        border-color: {contr_color};
        color: {word_color};
    }}
    .stButton > button:active {{
        background-color: {contr_color};
        border-color: {contr_color};
        color: {word_color};
    }}
</style>
""", unsafe_allow_html=True)

#    .stApp {{
#        max-width: 1200px;
#        margin: 0 auto;
#        background-color: {bgcolor};
#        padding: 0rem;
#        box-shadow: 0 0 10px rgba(0,0,0,0.1);
#    }}


def main():
    channels, gr_pvr, post_view, posts, subs, table_day_views = load_data()
    
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # БЛОК 1
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    
    head_col1, gap_col, head_col2 = st.columns([0.8, 0.01, 0.19])
    with head_col1:
         # Заголовок
        st.markdown('<div class="title"><h1>Simulative</h1></div>', unsafe_allow_html=True)
        # Подзаголовок
        st.markdown('<div class="subheader"><h2>Дашборд по анализу Telegram-каналов</h2></div>', unsafe_allow_html=True)
        # Выбор канала
        channels_list = sorted(posts['channel_name'].unique())
        selected_channel = st.selectbox('', channels_list) #'Выберите канал:', 

    with head_col2:
        # облако слов
        if selected_channel:
            df_words = prepare_data(posts, selected_channel)
            image = make_image(df_words, bgcolor, palette_num)
            st.image(image, use_container_width=True)



            # Инициализация состояния кнопок
    #if 'button_state' not in st.session_state:
    #    st.session_state.button_state = "all (6м)"

    # Создаем два разных состояния для двух графиков
    if 'button_state' not in st.session_state:
        st.session_state.button_state = "all (6м)"
    if 'heatmap_button_state' not in st.session_state:
        st.session_state.heatmap_button_state = "all (6м)"
    # Создаём отдельное состояние для таблицы
    if 'table_filter_state' not in st.session_state:
        st.session_state.table_filter_state = 14  # начальное значение


            #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # БЛОК 2
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
    
    #---------------------------------------------------------------------------------------------------------------------
    #Метрики

    st.write('')
    st.write('')
    mean_subs_pos, mean_subs_neg, max_subs_pos, max_subs_neg = calculate_mean_max_subs(subs,  selected_channel)
    mean_posts_day, mean_posts_week, mean_posts_month = calculate_mean_posts(posts, selected_channel)
    mean_views = calculate_mean_views(post_view,  selected_channel)
    mean_reacts, mean_idx, react1, perc1, react2, perc2, react3, perc3 = calculate_mean_reacts(gr_pvr,  selected_channel)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        image_subs = "word_subs.png"
        st.image(image_subs)
        st.write(f'<span class="custom-text"> 📈 Средний ежедневный прирост: </span><span class="custom-number">{mean_subs_pos}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 📉 Средний ежедневный отток: </span><span class="custom-number">{mean_subs_neg}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🚀 Максимальный прирост: </span><span class="custom-number">{max_subs_pos}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🆘 Максимальный отток: </span><span class="custom-number">{max_subs_neg}</span>', unsafe_allow_html=True)
    
    with col2:
        image_posts = "word_posts.png"
        st.image(image_posts)
        st.write(f'<span class="custom-text"> 📋 В среднем постов в день: </span><span class="custom-number">{mean_posts_day}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 📜 В среднем постов в неделю: </span><span class="custom-number">{mean_posts_week}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🗂️ В среднем постов в месяц: </span><span class="custom-number">{mean_posts_month}</span>', unsafe_allow_html=True)
    
    with col3:
        image_views = "word_active.png"
        st.image(image_views)        
        st.write(f'<span class="custom-text"> 👀 В среднем просмотров: </span><span class="custom-number">{mean_views}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🐾 В среднем реакций: </span><span class="custom-number">{mean_reacts}</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 💎 Средняя вовлеченность: </span><span class="custom-number">{mean_idx}%</span>', unsafe_allow_html=True)
    
    with col4:
        image_reacts = "word_reacts.png"
        st.image(image_reacts)        
        st.write(f'<span class="custom-text"> 🥇 Доля реакции {react1}: </span><span class="custom-number">{perc1}%</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🥈 Доля реакции {react2}: </span><span class="custom-number">{perc2}%</span>', unsafe_allow_html=True)
        st.write(f'<span class="custom-text"> 🥉 Доля реакции {react3}: </span><span class="custom-number">{perc3}%</span>', unsafe_allow_html=True)

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # БЛОК 3
    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # SLIDER
    slider = create_slider(slider_months_ago)

    #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    col1, gap_col, col2 = st.columns([0.47, 0.06, 0.47])
    with col1:
        #---------------------------------------------------------------------------------------------------------------------
        # график площадей - подписчики по дням
        
        st.markdown('<div class="subheader"><h2>Аудитория на момент измерения</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">График показывает изменение общего количества подписчиков с течением времени. Он помогает отслеживать динамику роста аудитории и выявлять периоды активного притока или оттока подписчиков. Анализ графика позволяет корректировать стратегию продвижения и создавать контент, который привлечет и удержит больше подписчиков. Процентные показатели индикаторов отражают изменения по сравнению с теми же показателями за предыдущие периоды. Сами периоды рассматриваются последовательно, как "скользящее окно", что позволяет отслеживать динамику изменений во времени.</div>', unsafe_allow_html=True)
        # Добавляем собственные стили для изменения внешнего вида слайдера
        st.markdown(""" <style> .stMultiSelect div[class^='select-all'] > input { display:none; } .stSlider > div > div > div[class^='st-b9'] > div > input[type='range'] { appearance: none; background-color: transparent; /* Цвет фона слайдера */ height: 10px; cursor: pointer; } /* Стиль для трекера */ .stSlider > div > div > div[class^='st-b9'] > div > input[type='range']::-webkit-slider-runnable-track { background-color: lightblue; /* Цвет трека */ height: 8px; border-radius: 15px; } /* Стиль для бегунков */ .stSlider > div > div > div[class^='st-b9'] > div > input[type='range']::-webkit-slider-thumb { appearance: none; background-color: red; /* Цвет бегунков */ border: 2px solid black; height: 18px; width: 18px; border-radius: 50%; margin-top: -6px; } </style> """, unsafe_allow_html=True)
        #slider_fig_subs = create_slider(subs, 'date', selected_channel, 'slider_fig_subs')
        try:
            fig_subs = create_fig_subs_inds(subs, selected_channel, slider , bgcolor, word_color, contr_color, graph_color)
            st.plotly_chart(fig_subs, use_container_width=True) 
        else:
            st.write('<span style="color:red;">🚨 график не собрался.</span>')
        

        #---------------------------------------------------------------------------------------------------------------------
        #гистограмма - динамика подписок
        
        st.markdown('<div class="subheader"><h2>Динамика подписок</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">Этот график показывает два ключевых показателя: количество пользователей, которые подписались на канал, и тех, кто отписался. Он помогает отслеживать, насколько эффективно ваш контент привлекает новую аудиторию и удерживает существующую. Анализируя этот график, можно сделать выводы о том, какие периоды были наиболее успешными в привлечении подписчиков, а также выявить моменты, когда наблюдалось значительное снижение аудитории. Этот анализ позволит вам скорректировать стратегию создания контента и время его публикации для достижения лучших результатов.</div>', unsafe_allow_html=True)
        # Кастомный CSS для скрытия подписей под слайдером
        st.markdown(""" <style> .stSlider .st-cl::after { content: ""; } </style> """, unsafe_allow_html=True)
        #slider = create_slider(subs, 'datetime', selected_channel, 'slider')
        try:
            fig_subs_pos_neg = create_subs_pos_neg(subs, selected_channel, slider, bgcolor, word_color, contr_color, graph_color, dark_color) 
            st.plotly_chart(fig_subs_pos_neg, use_container_width=True)
        else:
            st.write('<span style="color:red;">🚨 график не собрался.</span>')        
        

        #---------------------------------------------------------------------------------------------------------------------
        #пузырьковый график - интерес к контенту
        
        st.markdown('<div class="subheader"><h2>Визуализация интереса к контенту</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">На вертикальной оси (Y) показан индекс вовлеченности аудитории (реакции/просмотры), а горизонтальная ось (X) отражает количество просмотров. Размер пузырька соответствует объему текста: крупные пузырьки означают длинные тексты. Пузыри, расположенные выше, говорят о высоком интересе аудитории; низкие и маленькие пузырьки требуют внимания. Левая часть графика показывает материалы с большим количеством просмотров. Этот график помогает оценить популярность тем, найти способы улучшения менее успешных публикаций и повысить их привлекательность для аудитории.</div>', unsafe_allow_html=True)
        # Кнопки для выбора периода        
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        button_col1, button_col2, button_col3, button_col4, button_col5, button_gap = st.columns([0.05, 0.08, 0.08, 0.08, 0.10, 0.61])
        with button_col1:
            st.empty()          
        with button_col2:
            if st.button("3д", key="3db"):
                st.session_state.button_state = "3д"
        with button_col3:
            if st.button("1н", key="1wb"):
                st.session_state.button_state = "1н"
        with button_col4:
            if st.button("1м", key="1mb"):
                st.session_state.button_state = "1м"
        with button_col5:
            if st.button("all (6м)", key="6mb"):
                st.session_state.button_state = "all (6м)"
        st.markdown('</div>', unsafe_allow_html=True)

        # Фильтрация данных в зависимости от выбранной кнопки
        if st.session_state.button_state == "3д":
            filtered_bubble = gr_pvr[(gr_pvr.channel_name == selected_channel)&(pd.to_datetime(gr_pvr.post_datetime)>=date_ago('days', 2))]  
        elif st.session_state.button_state == "1н":
            filtered_bubble = gr_pvr[(gr_pvr.channel_name == selected_channel)&(pd.to_datetime(gr_pvr.post_datetime)>=date_ago('weeks', 1))]
        elif st.session_state.button_state == "1м":
            filtered_bubble = gr_pvr[(gr_pvr.channel_name == selected_channel)&(pd.to_datetime(gr_pvr.post_datetime)>=date_ago('months', 1))]
        else:  # "all (6м)"
            filtered_bubble = gr_pvr[(gr_pvr.channel_name == selected_channel)&(pd.to_datetime(gr_pvr.post_datetime)>=date_ago('months', 6))]

        if len(filtered_bubble ) != 0:
            fig_bubble = create_bubble_fig(filtered_bubble, slider, bgcolor, word_color, colors_gradient_bubble)
            if isinstance(fig_bubble, go.Figure):
                st.plotly_chart(fig_bubble, use_container_width=True)
            else:
                st.write('график не собрался')
        else:
            st.write('<span style="color:red;">🚨 По выбранному периоду график не может собраться. Проверьте дату обновления данных.</span>', unsafe_allow_html=True)

            #---------------------------------------------------------------------------------------------------------------------
        #Поисковик
        
        st.markdown('<div class="subheader"><h2>Просмотр текста поста и даты по номеру ID:</h2></div>', unsafe_allow_html=True)
        post_id = st.text_input("", "", placeholder = "Введите номер ID поста")
        if post_id:
            try:
                #row = posts.query(f"'id' == '{post_id}'").iloc[0]
                row = posts[posts.id.astype(str) == post_id].iloc[0, :]
                st.write(f"ID: {row['id']}")
                st.write(f"Дата: {row['date']}")
                st.write(f"Время: {row['time']}")
                st.write(f"Текст поста: {row['text']}")
                #st.write(f"Дата поста: {row['date']}")
            except IndexError:
                st.error("Номер ID не найден.")
 
        
    with col2:
        #---------------------------------------------------------------------------------------------------------------------
        # Гистограмма - публикации по дням с инидикаторами
        
        st.markdown('<div class="subheader"><h2>Суточные показатели публикаций</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">На графике представлена динамика публикаций, где каждая точка отражает количество за день. Рядом с графиком индикаторы, показывающие количество публикаций и их процентное изменение относительно предыдущих аналогичных периодов – дня, недели или месяца. Важно отметить, что эти периоды оцениваются скользящим образом, то есть они начинаются не с первого дня месяца или недели, а с текущего момента, что позволяет лучше понимать текущую тенденцию. Анализ помогает выявить изменения в частоте публикаций и может служить основой для корректировки собственных стратегий по созданию контента.</div>', unsafe_allow_html=True)
        #slider_fig_posts = create_slider(posts, 'date', selected_channel, 'slider_fig_posts')
        try:
            fig_posts = create_fig_posts_inds(posts, selected_channel, slider, bgcolor, word_color, contr_color, graph_color, color_Nx_size) 
            st.plotly_chart(fig_posts, use_container_width=True)
        else:
            st.write('<span style="color:red;">🚨 график не собрался.</span>')

        #---------------------------------------------------------------------------------------------------------------------
        #матрица - график публикаций
        
        st.markdown('<div class="subheader"><h2>График публикаций</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">Эта тепловая карта демонстрирует распределение публикаций по часам в течение суток. Ось X отображает временной диапазон от 1 до 24 часов, а ось Y — последовательность дат. Цветные ячейки символизируют моменты, когда выходили публикации, тогда как белые остаются незаполненными, указывая на отсутствие активности. С помощью этой карты легко заметить повторяющиеся схемы и подстроить свою стратегию публикаций так, чтобы они приносили максимум пользы.</div>', unsafe_allow_html=True)
       # Кнопки для выбора периода
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        button_col1, button_col2, button_col3, button_col4, button_col5, button_gap = st.columns([0.05, 0.08, 0.08, 0.08, 0.10, 0.61])
        with button_col1:
            st.empty()          
        with button_col2:
            if st.button("3д", key="3d"):
                st.session_state.heatmap_button_state = "3д"
        with button_col3:
            if st.button("1н", key="1w"):
                st.session_state.heatmap_button_state = "1н"
        with button_col4:
            if st.button("1м", key="1m"):
                st.session_state.heatmap_button_state = "1м"
        with button_col5:
            if st.button("all (6м)", key="6m"):
                st.session_state.heatmap_button_state = "all (6м)"
        st.markdown('</div>', unsafe_allow_html=True)

        # Фильтрация данных в зависимости от выбранной кнопки
        
        if st.session_state.heatmap_button_state == "3д":
            filtered_df = posts[(posts.channel_name == selected_channel) &
                                (pd.to_datetime(posts.date) >= date_ago('days', 2))]
        elif st.session_state.heatmap_button_state == "1н":
            filtered_df = posts[(posts.channel_name == selected_channel) &
                                (pd.to_datetime(posts.date) >= date_ago('weeks', 1))]
        elif st.session_state.heatmap_button_state == "1м":
            filtered_df = posts[(posts.channel_name == selected_channel) &
                                (pd.to_datetime(posts.date) >= date_ago('months', 1))]
        else:  # "all (6м)"
            filtered_df = posts[(posts.channel_name == selected_channel) &
                                (pd.to_datetime(posts.date) >= date_ago('months', 6))]

        # Отображение тепловой карты
        #st.plotly_chart(create_heatmap(filtered_df, bgcolor, word_color, min_color_heatmap, graph_color), use_container_width=True)
        
        if len(filtered_df) != 0:
            heatmap_min_dt, heatmap_max_dt = slider
            filtered_df = filtered_df[(pd.to_datetime(filtered_df.date).dt.date>= heatmap_min_dt)&(pd.to_datetime(filtered_df.date).dt.date<=heatmap_max_dt)]
            fig_heatmap = create_heatmap(filtered_df,  bgcolor, word_color, min_color_heatmap, graph_color)
            if isinstance(fig_heatmap, go.Figure):
                st.plotly_chart(fig_heatmap, use_container_width=True)
            else:
                st.write('график не собрался')
        else:
            st.write('<span style="color:red;">🚨 По выбранному периоду график не может собраться. Проверьте дату обновления данных.</span>', unsafe_allow_html=True)

        #---------------------------------------------------------------------------------------------------------------------
        #Таблица с постами Лидеры и оутсайдеры
        #st.pyplot(create_table_top5(posts, post_view, subs, gr_pvr,  selected_channel, bgcolor, word_color, cmap_colors))
        st.markdown('<div class="subheader"><h2>Лидеры и аутсайдеры среди постов</h2></div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-text">Данная таблица содержит рейтинг пяти лучших и пяти худших публикаций по ключевым показателям, включая количество просмотров, реакций, индекс вовлеченности и динамику подписок и отписок после конкретных публикаций. Проведение сравнительного анализа этих метрик позволит выявить типы контента, которые привлекают наибольшее внимание аудитории, стимулируют её активность и способствуют росту подписчиков.</div>', unsafe_allow_html=True)
        st.write('')
        
        try:
            create_table_top5(channels, posts, post_view, subs, gr_pvr,  selected_channel, slider, bgcolor, word_color, cmap_colors)
        else:
            st.write('<span style="color:red;">🚨 график не собрался.</span>')
    #---------------------------------------------------------------------------------------------------------------------
    # Таблица - динамика просмотров
        
    st.markdown('<div class="subheader"><h2>Динамика просмотров по дням</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-text">Эта таблица предназначена для определения оптимального времени размещения контента. Также таблица может помочь выявить, какие форматы контента привлекают больше просмотров в первые сутки, и сравнить их с другими форматами. Обратите внимание на разницу между утренними и вечерними публикациями, чтобы понять, когда ваша аудитория наиболее активна. Также следите за необычными скачками просмотров через несколько дней после публикации, так как это может указывать на подозрительную активность.</div>', unsafe_allow_html=True)
    
    try:
        # Слайдер для настройки диапазона дней
        days_to_show = st.slider(
            label="", 
            min_value=7, 
            max_value=72, 
            value=st.session_state.table_filter_state,
            key="slider_days",
        )
        st.session_state.table_filter_state = days_to_show  # сохраняем новое значение    
    
        #st.slider("", min_value=7, max_value=72, value=14, key="slider_days")
        #days_to_show = st.session_state.slider_days
        columns_to_show = [ "Дата публикации", "Текст поста","Текущие просмотры"] + [str(i)+" д" for i in range(1, days_to_show+1)]
        
        df = table_views(table_day_views, slider, days_to_show, selected_channel)
        # Преобразование слов в ссылки
        def make_link(row):
            return f'<a href="{row["Ссылка"]}" target="_blank">{row["Текст поста"]}</a>'
        
        df['Текст поста'] = df.apply(make_link, axis=1)
    
        df.index = df["ID поста"]
        df_subset = df[columns_to_show]
        
        html_table = styled_df(df_subset, '#666', contr_color).to_html()
        # Оборачиваем таблицу в div с фиксированной шириной и прокруткой
        scrollable_table = f'<div style="overflow-x: auto; overflow-y: auto; max-height: 700px;">{html_table}</div>'
        st.write(scrollable_table, unsafe_allow_html=True)  
    
        st.write('')
        st.write('')
        st.write('')
        st.write('<p style="text-align: center;">Источник: Данные Telegram API</p>', unsafe_allow_html=True)
        st.write('<p style="text-align: center;">Обработка данных и дашборд - Альмира (@a1m_ra), Парсинг данных - Вероника (@chacter)</p>', unsafe_allow_html=True)
    else:
        st.write('<span style="color:red;">🚨 график не собрался.</span>')

if __name__ == "__main__":
    main()


