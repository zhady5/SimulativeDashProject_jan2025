import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import random

# ОСНОВНЫЕ ХАРАКТЕРИСТИКИ КАНАЛА

# В среднем приходится просмотров на 1й день от всех просмотров
# В среднем приходится просмотров на 1ю неделю от всех просмотров
#-----------------------------Метрики по подписчикам-------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

def calculate_mean_max_subs(subs, channel):
    try:
        filtered_df = subs[subs.channel_name==channel][['date', 'day_change_pos', 'day_change_neg']].drop_duplicates()
        
        # вопрос по округлению!!!!!!!
        mean_subs_pos, mean_subs_neg = int(round(filtered_df.day_change_pos.mean(), 0)), int(round(filtered_df.day_change_neg.mean(), 0)) 
        max_subs_pos, max_subs_neg = int(round(filtered_df.day_change_pos.max(), 0)), int(round(filtered_df.day_change_neg.min(), 0)) 
        
        # Средний ежедневный прирост
        # Средний ежедневный отток    
        # Максимальный дневной прирост 
        # Максимальный дневной отток
        
        return mean_subs_pos, mean_subs_neg, max_subs_pos, max_subs_neg
    except:
        return 0,0,0,0

#-----------------------------Метрики по публикациям-------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

def calculate_mean_posts(posts, channel):
    try:
        filtered_df = posts[posts.channel_name==channel].copy()
        filtered_df.loc[:, 'date_week'] = pd.to_datetime(filtered_df.date).apply(lambda d: d.isocalendar().week)
        filtered_df.loc[:, 'date_month'] = filtered_df.date.apply(lambda d: str(d)[:7])
    
        mean_posts_day = int(round(filtered_df.cnt.sum()/len(pd.date_range(filtered_df.date.min(), filtered_df.date.max())), 0))
        mean_posts_week = int(round(filtered_df.groupby('date_week').cnt.sum().mean(), 0))
        mean_posts_month = int(round(filtered_df.groupby('date_month').cnt.sum().mean(), 0))
    
        # среднее количество публикаций в день
        # среднее количество публикаций в неделю
        # среднее количество публикаций в месяц
    
        return mean_posts_day, mean_posts_week, mean_posts_month
    except:
        return 0,0,0

#-----------------------------Метрики по просмотрам-------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

def calculate_mean_views(post_view, channel):
    try:
        filtered_df = post_view[post_view.channel_name==channel].copy()
        mean_views = int(round(filtered_df[['post_id', 'current_views']].drop_duplicates().current_views.mean(), 0))
        
        # Среднее количество просмотров одной публикации
        
        return mean_views 
    except:
        return 0

#-----------------------------Метрики по реакциям-------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------

def calculate_mean_reacts(gr_pvr, channel, react1='', perc1=0, react2='', perc2=0, react3='', perc3=0):
    try:
        filtered_df = gr_pvr[gr_pvr.channel_name == channel]
    
        filtered_df.loc[:,'reaction_type'] = filtered_df.reaction_type.apply(lambda r: 'Custom' if 'ReactionCustomEmoji' in r else r)
        filtered_df.loc[:,'reaction_type'] = filtered_df.reaction_type.apply(lambda r: 'Paid 🌟' if 'ReactionPaid' in r else r)
        
        mean_reacts = int(round(filtered_df[['post_id', 'react_cnt_sum']].drop_duplicates().react_cnt_sum.mean(), 0))
        mean_idx = round(filtered_df[['post_id', 'idx_active']].drop_duplicates().idx_active.mean(), 1)
        
        allReact = filtered_df.react_cnt.sum()
        top3react = filtered_df.groupby('reaction_type').react_cnt.sum().reset_index()\
                                .sort_values('react_cnt', ascending=False).head(3).reset_index()
        top3react.loc[:, 'react_cnt_perc'] = round(top3react.react_cnt/allReact*100, 0)
        cnt_react = top3react.shape[0]
        
        if cnt_react == 3:
            react1, perc1 = top3react.reaction_type[0], int(top3react.react_cnt_perc[0])
            react2, perc2 = top3react.reaction_type[1], int(top3react.react_cnt_perc[1])
            react3, perc3 = top3react.reaction_type[2], int(top3react.react_cnt_perc[2])
        elif cnt_react == 2:
            react1, perc1 = top3react.reaction_type[0], int(top3react.react_cnt_perc[0])
            react2, perc2 = top3react.reaction_type[1], int(top3react.react_cnt_perc[1])
        elif cnt_react == 1:
            react1, perc1 = top3react.reaction_type[0], int(top3react.react_cnt_perc[0])
    
        # Среднее количество реакций на публикацию
        # Средний индекс активности
        # 3 самых популярных реакий и их доли от всех реакций 
    
        return mean_reacts, mean_idx, react1, perc1, react2, perc2, react3, perc3
    except:
        return 0,0,0,0,0,0,0,0
