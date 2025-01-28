import pandas as pd

# OLD VERSION WITHOUT text_short and link

#def create_table(post_view):
#  #groupping
#  group_cols = ['channel_name', 'post_id', 'post_datetime', 'current_views', 'days_diff']
#  tab = post_view.groupby(group_cols)[['view_change']].sum().reset_index()
#  
#  #tab_abs
#  pivot_idxs = ['channel_name', 'post_id', 'post_datetime', 'current_views']
#  tab_abs = tab.pivot(index=pivot_idxs , columns='days_diff', values='view_change').reset_index().fillna(0)
#  
#  #tab_perc
#  tab_perc = tab_abs.copy()
#  tab_perc[tab_perc.columns[4:]] /= tab_perc['current_views'].values[:, None] 
#  tab_perc[tab_perc.columns[4:]] = tab_perc[tab_perc.columns[4:]].apply(lambda n: round(n*100, 2))
#
#  # Объединение числовых столбцов с добавлением процентов
#  numeric_columns = tab_perc.columns[4:]
#  df_abs = tab_abs.copy()
#  df_percent = tab_perc.copy()
#  # Объединение числовых столбцов с добавлением процентов
#  merged_numeric = df_abs[numeric_columns].astype(str).copy()
#  for index, row in merged_numeric.iterrows():
#      for column in numeric_columns:
#          value = row[column]
#          percent_value = df_percent.at[index, column]
#          merged_numeric.at[index, column] = f"{value} ({percent_value}%)"
#
#  tab_final = pd.concat([tab_abs[tab_abs.columns[:4]], merged_numeric], axis=1).sort_values(by = 'post_datetime', ascending=False)
#
#  return tab_final


def create_table(channels, posts, post_view):
    posts_un = posts.merge(channels[['id', 'username']].rename(columns={'id':'channel_id'}), on = 'channel_id').copy()
    posts_un.loc[:, 'text_short'] = posts.text.str[:20]
    posts_un.loc[:, 'link'] = 'https://t.me/' +  posts_un.username + '/'+ posts_un.id.astype(str)
    post_view = post_view.merge(posts_un[['id', 'text_short', 'link']].rename(columns={'id':'post_id'}), on = 'post_id')
    #groupping
    group_cols = ['channel_name', 'post_id', 'text_short', 'link', 'post_datetime', 'current_views', 'days_diff']
    tab = post_view.groupby(group_cols)[['view_change']].sum().reset_index()
    #tab_abs
    pivot_idxs = ['channel_name', 'post_id', 'text_short', 'link', 'post_datetime', 'current_views']
    tab_abs = tab.pivot(index=pivot_idxs , columns='days_diff', values='view_change').reset_index().fillna(0)
    #tab_perc
    tab_perc = tab_abs.copy()
    # Создаем новый список колонок без исключенных
    numeric_columns = [col for col in tab_perc.columns if col not in pivot_idxs ]
    tab_perc[numeric_columns] /= tab_perc['current_views'].values[:, None]
    tab_perc[numeric_columns] = tab_perc[numeric_columns].apply(lambda n: round(n*100, 2))
    # Объединение числовых столбцов с добавлением процентов
    df_abs = tab_abs.copy()
    df_percent = tab_perc.copy()
    # Объединение числовых столбцов с добавлением процентов
    merged_numeric = df_abs[numeric_columns].astype(str).copy()
    for index, row in merged_numeric.iterrows():
        for column in numeric_columns:
            value = row[column]
            percent_value = df_percent.at[index, column]
            merged_numeric.at[index, column] = f"{value} ({percent_value}%)"
    
    tab_final = pd.concat([tab_abs[pivot_idxs], merged_numeric], axis=1).sort_values(by = 'post_datetime', ascending=False)

    return tab_final