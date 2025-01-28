import datetime
from dateutil.relativedelta import relativedelta
from PIL import ImageColor
import pandas as pd
import random

def date_ago(tp, num=0):
    if tp == 'today':
        return datetime.datetime.now().strftime("%Y-%m-%d") 
    elif tp == 'yesterday':
        return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif tp == 'days':
        return (datetime.datetime.now() - datetime.timedelta(days=num+1)).strftime("%Y-%m-%d")
    elif tp == 'weeks':
        return (datetime.datetime.now() - datetime.timedelta(days= 7*num + 1)).strftime("%Y-%m-%d") 
    elif tp == 'months':
        return (datetime.datetime.now() - relativedelta(months=num) - datetime.timedelta(days=1)).strftime("%Y-%m-%d") 
    else:
        print('Неправильно задан тип даты или не указано количество повторений (возможные типы дат: today, yesterday, days, weeks, months')

def convert_date(date, format_date = '%Y-%m-%d %H:%M:%S.%f'):
    try:
        return datetime.datetime.strptime(date, format_date)
    except ValueError:
        # Если строка не может быть преобразована в дату, возвращаем NaT (Not a Time)
        return pd.NaT


def get_current_previous_sums(df, col, period):
    mask1 = (df.date.apply(lambda d: convert_date(d, '%Y-%m-%d').date()) <= convert_date(date_ago(period[0]), '%Y-%m-%d').date())
    mask2 = (df.date.apply(lambda d: convert_date(d, '%Y-%m-%d').date()) > convert_date(date_ago(period[1], period[2]), '%Y-%m-%d').date())
    mask3 = (df.date.apply(lambda d: convert_date(d, '%Y-%m-%d').date()) <= convert_date(date_ago(period[1], period[2]), '%Y-%m-%d').date())
    mask4 = (df.date.apply(lambda d: convert_date(d, '%Y-%m-%d').date()) > convert_date(date_ago(period[1], period[2]*2), '%Y-%m-%d').date())
    
    current = df[mask1&mask2][col].sum()
    previous = df[mask3&mask4][col].sum()    
    
    return current, previous


# Функция для определения градиентной заливки
def get_gradient_color(value, min_val=0, max_val=100):
    # Если значение равно нулю, возвращаем прозрачный цвет
    if value == 0:
        return "transparent"
    
    # Рассчитываем процентное соотношение между минимальным и максимальным значением
    ratio = (value - min_val) / (max_val - min_val)
    # Ограничиваем диапазон значений
    ratio = max(min(ratio, 1), 0)

     # Начальные и конечные значения RGB
    start_r, start_g, start_b = 139, 0, 0 #245, 223, 191  # Бежевый (#f5dfbf)
    end_r, end_g, end_b = 34, 139, 34          # Зелёный (#228B22)
    
    # Рассчитываем промежуточные значения RGB
    r = int(start_r * (1 - ratio) + end_r * ratio)
    g = int(start_g * (1 - ratio) + end_g * ratio)
    b = int(start_b * (1 - ratio) + end_b * ratio)
    
    color = '#%02x%02x%02x' % (r, g, b)
    return color


def hex_to_rgb(hex_code):
    """Преобразует HEX-код в RGB."""
    rgb = ImageColor.getcolor(hex_code, "RGB")
    return rgb

def interpolate_color(start_color, end_color, steps):
    """Интерполирует цвет между двумя значениями RGB."""
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color
    step_r = (end_r - start_r) / steps
    step_g = (end_g - start_g) / steps
    step_b = (end_b - start_b) / steps
    return [(int(start_r + i * step_r),
             int(start_g + i * step_g),
             int(start_b + i * step_b)) for i in range(steps)]

def gradient_color_func(start_color = '#8B0000', end_color = '#ffb347', word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    start_color = hex_to_rgb(start_color)
    end_color = hex_to_rgb(end_color)
    num_steps = 50  # Количество шагов равно количеству слов
    colors = interpolate_color(start_color, end_color, num_steps)
    index = random.randint(0, num_steps - 1)  # Случайное число от 0 до количества слов
    r, g, b = colors[index]
    return f"rgb({r}, {g}, {b})"



