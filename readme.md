
## Описание проекта
Бот разрабатывался для покупки билетов на мероприятия Фестиваля управленческого мастерства в 2024 году Тесеем. Стек приложения: aiogram 3, sqlalchemy, docker, PostgrSQL. также в контейнере присутсвует pgAdmin.

## Полезные ссылки
[Руководство пользователя](./docs/userToutorial.md)

### Ссылки для разработчика
[Руководство по aiogram 3](https://mastergroosha.github.io/aiogram-3-guide/)
[Хабр, Создаем начальную миграцию для alembic](https://habr.com/ru/articles/585228/)

# Запуск проекта
## Локальное окружение
1. активировать окружение и за папки .venv/Scripts/activate
2. выполнить  `pip install -r requirements.txt` для установки зависимостей
3. добавить токен доступа в файл .env  `BOT_TOKEN = token` и все остальные переменные, файлы из раздела "переменные среды"
4. заполнить в .env файл.
5. добавить id чата группы администраторов в .env `admin_group = -6000`
6. добавить бота в группу администраторов, назначить админом (иначе не будет реагировать на команды)
> перед запуском убедиться в наличии всех FT в базе данных, так как их отсутсвие сломает бот в любой момент
7. запустить приложение: `py bot.py`

## Запуск приложения в Docker
`docker compose --env-file .test.env up -d`

пересобрать только бота:

`docker compose --env-file .test.env  up -d  --no-deps --build bot`

# Настройка проекта

## миграции, работа с базой данных
Миграции на "проде" применяются с помощью команды `alembic upgrade head` зашитой в Dockerfile, затем происходит запуск бота

### добавление миграции
`alembic revision --autogenerate -m "Added account table"`
### применение миграции
`alembic upgrade head`

### добавление пакетов
после установки пакета pip install сделать 
`pip freeze' и зафиксировать версию в requirements.txt

### Переменные среды
Для проекта необходим файл .env содержащий следующие переменные:

BOT_TOKEN = "{botToken}"

connection_string = "postgresql+psycopg2://paymentBot:paymentBot@postgres:5432/fum2024_test"

admin_group = "{adminGroupId}"

PGADMIN_DEFAULT_EMAIL = "a@mail.ru"

PGADMIN_DEFAULT_PASSWORD = "pgAdmin"

POSTGRES_DB = "fum2024_test"

POSTGRES_USER = "user"

POSTGRES_PASSWORD = "pwd"

dbVolumeName = "paymentBot-db-test"

pgAdminVolumeName = "paymentBot-dbAdmin-test"

PARTNER_EVENT_ID = "5" # эта переменная реализована специально для вкладки "хочу стать партнером". Так как Id фестиваля разный, ничего лучше не придумал чем конфигурировать таким образом

ENVIRONMENT = "development" #ввел для использования developmentHandler

GOOGLECREDENTIALS = "googleCredentials.json" - путь к файлу с настройками гугл проекта

GOOGLESHEET = "fum2024test" -рабочий документ, в который будет записываться информация о билетах. Предварительно документу дать права на запись для пользователя из под которого работает бот

Переменные могут быть использованы в файле compose.yaml, также **должны быть определены в config_reader.py**
Также все эти переменные должны быть определены в compose.yaml, так как в контейнер попадают именно благодаря ему

### Интеграция с google Sheets
Правила настройки таблицы google:
1. Создать таблицу, дать доступ на редактирование сервисному аккаунту, передать название таблицы в переменную GOOGLESHEET
2. в проекте должен быть  googleCredentials.json со всеми необходимыми параметрами для доступа к api гугла

# База данных, модели
## модель UserRequest свойство status:
 0 - новый запрос, не подтвержденный

 1 - подтвержденный запрос, ожидает оплаты

 2 - оплаченный запрос

 3 - анулированный (этот статус проставляется 0 и 1, если пользователь кликнул /start)
