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
├── api.py
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
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
- Документация Swagger: http://localhost:8000/docs

### Конфигурация

Все параметры (строки подключения, пути) описаны в `config.yaml`. Пример структуры:
```yaml
db:
  server: "SERVER_NAME"
  database: "ERP_Agent"
  trusted_connection: true

 ecom:
  server: "ECOM_SERVER"
  database: "ecom_db"

 paths:
  input_dir: "/data/invoices"
  output_dir: "/data/xmls"
  log_file: "/var/log/qualification-work.log"
```

### Тестирование

```bash
pytest --cov
```
