## Qualification Work

Автоматизированная система обработки входящих табличных файлов счетов-фактур и генерации XML для интеграции с учётными системами.

### Описание

Проект считывает данные из текстовых файлов-счётов (разделитель `|`), подтягивает дополнительные данные из баз данных (`db` и `ecom`), обрабатывает и группирует записи, рассчитывает суммы и налоги, после чего формирует корректные XML-файлы для дальнейшей передачи.

### Основные возможности

- Парсинг табличных текстовых файлов счётов-фактур
- Получение дополнительных данных об организациях и счетах из двух баз данных
- Генерация единичных и пакетных XML-файлов по шаблонам
- CLI-утилиты для одноразового (`runner.py`) и периодического (`scheduler.py`) запуска
- REST API на FastAPI для получения списка и скачивания сгенерированных XML
- Набор модульных тестов для ключевых компонентов

### Примерная структура проекта

```
Qualification-Work/           # Корень репозитория
├── README.md                 # Описание проекта и инструкции
├── config.yaml               # Настройки подключения и пути
├── Qualification Work.sln    # Решение для Visual Studio
├── Qualification Work.pyproj # Проект Python
├── core/                     # Парсинг и основная логика обработки файлов
│   ├── invoice.py            # Класс Invoice, чтение и преобразование данных
│   └── main.py               # Батч- и одиночная обработка, логирование
├── db/                       # Работа с SQL Server (ERP_Agent)
│   ├── db.py                 # Класс Database на pyodbc
│   └── utils.py              # Утилиты для запросов и преобразований
├── ecom/                     # Работа с ecom-базой
│   ├── db.py                 # ReadOnlyDatabase, возвращает DataFrame/список словарей
│   └── utils.py              # fetch_ecom_data(account)
├── xmlgen/                   # Формирование XML из шаблонов
│   ├── template.py           # Загрузка шаблонов
│   └── generator.py          # Заполнение и сохранение XML
├── scripts/                  # Утилиты запуска
│   ├── runner.py             # Одноразовый запуск обработки
│   └── scheduler.py          # Планировщик (каждые 10 минут)
├── server.py                 # FastAPI
├── tests/                    # Модульные тесты
│   ├── test_core             # Тесты для core-модулей
│   ├── test_db               # Заготовки тестов для db
│   ├── test_ecom             # Заготовки тестов для ecom
│   ├── test_xmlgen           # Тестирование генерации XML
│   └── test_api              # Тесты API
└── requirements.txt          # Список зависимостей
```

### Установка и запуск

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/k1selekn/Qualification-Work.git
   cd Qualification-Work
   ```

2. Установите зависимости (рекомендуем использовать виртуальное окружение):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\\Scripts\\activate # Windows
   pip install -r requirements.txt
   ```

3. Настройте подключение к БД и пути в `config.yaml`.

### Примеры запуска

#### Одноразовая обработка (runner)
```bash
python scripts/runner.py --input /path/to/invoices --output /path/to/xmls
```
Параметры можно опустить — тогда будут использованы значения из `config.yaml`.

#### Периодический запуск (scheduler)
```bash
python scripts/scheduler.py
```
Сценарий будет проверять наличие новых файлов каждые 10 минут.

#### REST API (FastAPI)
```bash
py -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```
- Для Swagger-UI:
http://127.0.0.1:8000/docs

- Для ReDoc:
http://127.0.0.1:8000/redoc

- Чистый OpenAPI-спецификатор (JSON):
http://127.0.0.1:8000/openapi.json

- Панель администратора:
http://127.0.0.1:8000/admin/dashboard

### Конфигурация

Все параметры (строки подключения, пути) описаны в `config.yaml`. Пример структуры:
```yaml
# config.yaml
db:
  server: "kiselek"
  database: "FinalQW"
  driver: "ODBC Driver 18 for SQL Server"
  instance: ""
  port: 1433
  trusted: true
  uid: ""
  pwd: ""
  autocommit: true

ecom_db:
  server: "kiselek"
  database: "ECOM"
  driver: "ODBC Driver 18 for SQL Server"
  instance: ""
  port: 1433
  trusted: true
  uid: ""
  pwd: ""
  autocommit: true

paths:
  input_folder: "data/in"
  output_folder: "data/out"
  logs_folder: "logs"

api:
  base_url: "http://localhost:8000"
  api_key: "kiselek"
```

### Тестирование

```bash
pytest --cov
```
