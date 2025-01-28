## Дашборд можно посмотреть тут: [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://simulativedashprojectdec2024.streamlit.app/)  


### SimulativeDashProject_dec2024/

├── `.github/workflows/`      # Конфигурации GitHub Actions

│   └── `main.yml`            # Основной файл конфигурации CI/CD

├── `graph_functions/`        # Функции для создания графиков

│   └── `**init**.py`         # Инициализация модуля графических функций

├── `preparation_data/`       # Скрипты обработки данных

│   └── `data_processing.py`  # Основной скрипт обработки данных

├── `prepared_tables/`        # Обработанные таблицы

│   └── `table_day_views.csv` # Пример обработанной таблицы

├── `app.py`                  # Основной файл приложения

├── `Procfile`                # Конфигурация для развертывания (например, на Heroku)

├── `requirements.txt`        # Список зависимостей Python

└── `stopwords-ru.txt`        # Список стоп-слов для русского языка

└── `palettes.txt`            # Список палеток для окрашивания слов в облаке слов


## Требования

- Python 3.7 или выше
- Зависимости из файла `requirements.txt`, включая:
  - pandas
  - numpy
  - plotly
  - dash
  - (другие зависимости, указанные в файле)

## Инструкция по установке

1. Клонирование репозитория:
  git clone [https://github.com/zhady5/SimulativeDashProject_dec2024.git](https://github.com/zhady5/SimulativeDashProject_dec2024.git)
  cd SimulativeDashProject_dec2024
2. Создание виртуального окружения:
  python -m venv venv
  source venv/bin/activate  # Для Windows: venv\Scripts\activate
3. Установка зависимостей:
  pip install -r requirements.txt
4. Note:
   в файле `preparation_data/schedule_load_data.py` поменять значения переменных `repo_owner`, `repo_name`, `branch`

## Обработка данных

- `preparation_data/`: Скрипты для загрузки из БД и предварительной обработки данных.
- `graph_functions/`: Содержит функции для создания различных типов графиков и визуализаций.
- Обработанные данные сохраняются в директории `prepared_tables/` для дальнейшего использования в дашборде.

## Рабочие процессы (CI/CD)

Проект использует GitHub Actions для автоматизации процессов: `.github/workflows/main.yml


