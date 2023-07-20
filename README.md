# CarWebBot

![Screenshot 2023-07-20 at 17-52-53 CarWebBot](https://github.com/SerHappy/CarWebBot/assets/57107119/60713d6e-798e-4f13-926d-5fc2214726fc)

## Описание проекта

CarWebBot - это веб-сервер на Django, который обеспечивает функциональность для управления контентом Telegram канала. Администраторы могут создавать, редактировать и удалять объявления, которые затем публикуются в телеграмм канале.

## Основные функции

* Создание, редактирование и удаление объявлений для публикации в Telegram канале
* Возможность добавлять неограниченное количество изображений и видео к сообщениям
* Отложенные объявления

## Технологии

* Python 3.11
* Django
* MySQL
* Redis
* Gunicorn
* Nginx
* Celery
* Telegram Bot API
* AJAX
* HTML
* CSS
* Bootstrap
* JavaScript
* Dropzone.js
* Datepicker.js
* Select2.js

## Инструкция по развертыванию проекта (Ubuntu server)

### Шаг 1: Подготовка

Обновите вашу систему:

```bash
sudo apt update
sudo apt upgrade
```

Установите Python 3.11:

```bash
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.11
```

Установите необходимые пакеты

```bash
sudo apt install python3-pip libpython3.11-dev libmysqlclient-dev libssl-dev mysql-server default-libmysqlclient-dev nginx curl redis-server
```

### Шаг 2: Установка Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Добавьте Poetry в вашу PATH переменную ([документация](https://python-poetry.org/docs/)).

Сконфигурируйте Poetry так, чтобы он создавал виртуальное окружение внутри проекта:

```bash
poetry config virtualenvs.in-project true
```

### Шаг 3: Клонирование вашего проекта с GitHub

```bash
cd /var/www
git clone https://github.com/SerHappy/CarWebBot.git
```

### Шаг 4: Установка зависимостей проекта

```bash
cd CarWebBot
poetry install
```

### Шаг 5: Настройка переменных окружения

Текущий проект использует файл `.env` для управления переменными окружения. Для того чтобы проект работал корректно, нужно создать этот файл и заполнить его правильными значениями.

```bash
cd /var/www/CarWebBot/web
mv .env-example .env
nano .env
```

Добавьте в файл следующие значения (замените `value` на соответствующие значения для вашего проекта):

```bash
SECRET_KEY = value
ALLOWED_HOSTS = value
DEBUG = value
TELEGRAM_BOT_TOKEN = value
CHANNEL_ID = value
CHANNEL_NAME = value
LOGURU_PATH = value
LOGURU_LEVEL = value
LOGURU_FORMAT = value
BASE_URL = value
DB_ENGINE = value
DB_NAME = value
DB_USER = value
DB_PASSWORD = value
DB_HOST = value
DB_PORT = value
CELERY_BROKER_URL = value
MEDIA_CHANNEL_ID = value
```

Описание каждого ключа:

* `SECRET_KEY`: Это секретный ключ Django для вашего проекта. Он используется для предоставления криптографической подписи и должен быть сохранен в безопасности. Не делитесь им и не выкладывайте в открытый доступ.
   > Пример: `"your-django-secret-key"`.

* `ALLOWED_HOSTS`: Это список хостов/доменов, на которых будет работать ваш проект Django.
   > Пример: `127.0.0.1, your-server-ip, localhost`.

* `DEBUG`: Этот параметр указывает, должен ли Django использовать режим отладки. Если это значение `True`, Django будет отображать подробные сообщения об ошибках.
   > Пример: `True` или `False`.

* `TELEGRAM_BOT_TOKEN`: Токен вашего бота Telegram.
   > Пример: `"your-telegram-bot-token"`.

* `CHANNEL_ID`: Идентификатор канала Telegram, на который бот будет отправлять сообщения.
   > Пример: `"your-channel-id"`.

* `CHANNEL_NAME`: Имя канала Telegram, на который бот будет отправлять сообщения.
   > Пример: `"your-channel-name"`.

* `MEDIA_CHANNEL_ID`: Идентификатор канала Telegram, на который бот будет загружать медиафайлы.
   > Пример: `"your-media-channel-id"`.

* `LOGURU_PATH`: Путь до файла логов для Loguru, инструмента логирования Python.
   > Пример: `"/path/to/your/logfile.log"`.

* `LOGURU_LEVEL`: Уровень логирования для Loguru.
   > Пример: `"DEBUG"` или `"INFO"`.

* `LOGURU_FORMAT`: Формат логирования для Loguru.
   > Пример: `"<green>{time:DD.MM.YYYY HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"`.

* `BASE_URL`: Базовый URL вашего сервера. Это основной адрес, который будет использоваться для доступа к вашему серверу.
   > Пример: `"http://your-server-ip:8000"`.

* `DB_ENGINE`: Движок базы данных Django, который вы будете использовать.
   > Пример: `"django.db.backends.mysql"` для MySQL.

* `DB_NAME`: Имя вашей базы данных.
   > Пример: `"your-database-name"`.

* `DB_USER`: Имя пользователя для доступа к вашей базе данных.
   > Пример: `"your-database-user"`.

* `DB_PASSWORD`: Пароль для доступа к вашей базе данных.
   > Пример: `"your-database-password"`.

* `DB_HOST`: Хост вашей базы данных. Если ваша база данных находится на том же сервере, что и ваш проект Django, вы можете использовать "localhost".
   > Пример: `"localhost"` или `"your-database-server-ip"`.

* `DB_PORT`: Порт вашей базы данных.
   > Пример: `3306`.

* `CELERY_BROKER_URL`: URL брокера для Celery. Celery - это асинхронная очередь задач, которую можно использовать для выполнения задач в фоновом режиме.
   > Пример: `"redis://localhost:6379"`.

Сохраните и закройте файл.

### Шаг 6: Настройка MySQL

Запустите скрипт безопасной установки для MySQL:

```bash
sudo mysql_secure_installation
```

Войдите в MySQL:

```bash
sudo mysql
```

Создайте базу данных:

```bash
CREATE DATABASE cars;
```

Если вы столкнулись с ошибкой при установке MySQL ("SET PASSWORD has no significance for user 'root'@'localhost'"), выполните следующую команду:

```bash
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password by 'password';
```

Выйдите из MySQL:

```bash
exit;
```

Создайте и примените миграции:

```bash
cd /var/www/CarWebBot
poetry run python3.11 web/manage.py migrate
```

### Шаг 7: Настройка Redis

Отредактируйте конфигурацию Redis:

```bash
sudo nano /etc/redis/redis.conf
```

Замените строку `supervised no` на `supervised systemd`.

Перезапустите Redis:

```bash
sudo systemctl restart redis.service
```

### Шаг 8: Настройка Gunicorn

Создайте новый файл gunicorn.service:

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Добавьте следующие строки в файл:

```bash
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root


Group=www-data
WorkingDirectory=/var/www/CarWebBot/web
ExecStart=/var/www/CarWebBot/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/CarWebBot/web/CarWebBot.sock core.wsgi:application

[Install]
WantedBy=multi-user.target
```

Запустите Gunicorn и добавьте его в автозагрузку:

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### Шаг 9: Настройка Nginx

Создайте новый файл конфигурации Nginx:

```bash
sudo nano /etc/nginx/sites-available/CarWebBot
```

Добавьте следующие строки в файл, заменив `your_domain` на ваш домен:

```bash
server {
    listen 80;
    server_name your_domain;
    client_max_body_size 0;


 access_log /var/log/nginx/access.log;

    location /static/ {
        alias /var/www/CarWebBot/web/static/;
    }

    location /media/ {
        alias /var/www/CarWebBot/web/media/;
    }

    location / {
        proxy_pass http://unix:/var/www/CarWebBot/web/CarWebBot.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Создайте символическую ссылку на файл конфигурации Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/CarWebBot /etc/nginx/sites-enabled/
```

Проверьте наличие ошибок в конфигурации Nginx:

```bash
sudo nginx -t
```

Если все в порядке, перезапустите Nginx:

```bash
sudo systemctl restart nginx
```

### Шаг 10: Настройка Celery и Celery Beat

Создайте новый файл celery.service:

```bash
sudo nano /etc/systemd/system/celery.service
```

Добавьте следующие строки в файл:

```bash
[Unit]
Description=Celery Service
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/CarWebBot/web
ExecStart=/var/www/CarWebBot/.venv/bin/celery -A core worker --loglevel=info

[Install]
WantedBy=multi-user.target
```

Запустите службу Celery:

```bash
sudo systemctl start celery
sudo systemctl enable celery
```

Создайте новый файл celerybeat.service:

```bash
sudo nano /etc/systemd/system/celerybeat.service
```

Добавьте следующие строки в файл:

```bash
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/CarWebBot/web
ExecStart=/var/www/CarWebBot/.venv/bin/celery -A core beat --loglevel=info

[Install]
WantedBy=multi-user.target
```

Запустите службу Celery Beat:

```bash
sudo systemctl start celerybeat
sudo systemctl enable celerybeat
```

После завершения этих шагов, проект должен быть развернут и готов к использованию.
