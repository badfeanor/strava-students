# Анализ активностей студентов Strava

Проект для выгрузки и анализа последних 10 активностей студентов из Strava API.

## Описание

Скрипт выполняет следующие функции:
- Автоматическая аутентификация через Strava API с использованием OAuth 2.0
- Получение последних 10 активностей для каждого студента
- Сохранение данных в CSV файл с подробной информацией о каждой активности

## Требования

- Python 3.9+
- Docker и Docker Compose (опционально)

## Установка и настройка

### 1. Клонирование репозитория
```bash
git clone https://github.com/badfeanor/strava-students.git
cd strava-students
```

### 2. Настройка Strava API

1. Создайте приложение в Strava:
   - Перейдите на https://www.strava.com/settings/api
   - Создайте новое приложение
   - Сохраните Client ID и Client Secret

2. Создайте файл `.env` в корневой директории проекта:
```
STRAVA_CLIENT_ID=ваш_client_id
STRAVA_CLIENT_SECRET=ваш_client_secret
```

При первом запуске скрипт автоматически:
1. Откроет браузер для авторизации
2. Запросит необходимые права доступа
3. Получит и сохранит refresh token

### 3. Настройка списка студентов

1. Скопируйте пример конфигурационного файла:
```bash
cp config.example.py config.py
```

2. Отредактируйте файл `config.py`, добавив ID студентов Strava:
```python
STUDENT_IDS = [
    123456789,  # ID студента 1
    987654321,  # ID студента 2
    # ...
]
```

## Использование

### Запуск через Docker (рекомендуется)

1. Создайте директорию для результатов:
```bash
mkdir output
```

2. Запустите приложение:
```bash
docker-compose up --build
```

### Запуск без Docker

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите скрипт:
```bash
python strava_activities.py
```

## Результаты

Скрипт создает файл `output/student_activities.csv` со следующей информацией:
- Название активности
- Тип активности
- Расстояние (км)
- Время в движении (минуты)
- Общее время (минуты)
- Общий набор высоты (метры)
- Дата начала
- Средняя скорость (км/ч)
- Максимальная скорость (км/ч)
- ID спортсмена

## Структура проекта

```
strava-students/
├── .env                    # Конфигурация API (не включен в git)
├── .gitignore             # Исключения для git
├── config.example.py      # Пример конфигурационного файла
├── config.py             # Конфигурация со списком студентов (не включен в git)
├── Dockerfile            # Конфигурация Docker
├── README.md            # Документация
├── docker-compose.yml   # Конфигурация Docker Compose
├── output/              # Директория для результатов
├── requirements.txt     # Зависимости Python
└── strava_activities.py # Основной скрипт
```

## Лицензия

MIT 