# CarWebBot

![Screenshot 2023-07-22 at 20-42-56 CarWebBot](https://github.com/SerHappy/CarWebBot/assets/57107119/2861cdb3-d19d-42b6-85a1-0d46289de4bf)

## Описание проекта

CarWebBot - это веб-сервер на Django, который обеспечивает функциональность для управления контентом Telegram канала. Администраторы могут создавать, редактировать и удалять объявления, которые затем публикуются в телеграмм канале.

## Основные функции

* Создание, редактирование и удаление объявлений для публикации в Telegram канале
* Возможность добавлять неограниченное количество изображений и видео к сообщениям
* Отложенные объявления

## Технологии

### Бэкенд

* Python 3.11
* Django 4.2
* MySQL
* Redis
* Celery (В связке с Celery Beat)
* Gunicorn
* Telethon (вместо Telegram Bot API)
* Nginx

### Фронтенд

* HTML
* CSS
* JavaScript
* Bootstrap
* Dropzone.js
* Datepicker.js
* Select2.js
* AJAX

### Окружение и инфраструктура

* Docker
* Docker Compose

## Оглавление

* [Ручная установка на сервере (Ubuntu server)](#ручная-установка-на-сервере)
* [Автоматизированная установка с Docker (рекомендованный метод)](#автоматизированная-установка-с-docker)

## Ручная установка на сервере

Этот метод подразумевает вручную настройку всех компонентов на сервере. Вам потребуется установить все необходимые зависимости, настроить базу данных, запустить сервисы и т.д.

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
cp .env.example .env
nano .env
```

Отредактируйте файл `.env` и заполните его правильными значениями.

Обязательные переменные:

```bash
SECRET_KEY = value
ALLOWED_HOSTS = value
MAIN_CHANNEL_ID = value
MAIN_CHANNEL_NAME = value
TELETHON_API_ID = value
TELETHON_API_HASH = value
```

Необязательные переменные (для тестирования и разработки; не подходят для продакшена):

```bash
DEBUG = value # по умолчанию: True
LOGURU_FOLDER = value # по умолчанию: "logs/"
LOGURU_LEVEL = value # по умолчанию: "DEBUG"
LOGURU_FORMAT = value # по умолчанию: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
DB_ENGINE = value # по умолчанию: "django.db.backends.mysql"
DB_NAME = value # по умолчанию: "cars"
DB_USER = value # по умолчанию: "root"
DB_PASSWORD = value # по умолчанию: "root"
DB_HOST = value # по умолчанию: "localhost"
DB_PORT = value # по умолчанию: 3306
CELERY_BROKER_URL = value # по умолчанию: "redis://localhost:6379"
TELETHON_SESSION_NAME = value # по умолчанию: "session.session"
TELETHON_SYSTEM_VERSION = value # по умолчанию: "4.16.30-vxCUSTOM"
LOGIN_URL = value # по умолчанию: "/users/login/"
ANNOUNCEMENT_LIST_PER_PAGE = value # по умолчанию: 5
TAG_LIST_PER_PAGE = value # по умолчанию: 10
```

Обратите внимание:

* Обязательные переменные должны быть настроены правильно, иначе проект не будет работать корректно.
* Дефолтные настройки необязательных переменных предназначены для тестирования и разработки. Перед деплоем в продакшн убедитесь, что они настроены в соответствии с вашими потребностями и соответствуют требованиям безопасности.

Описание каждого ключа вы можете найти ниже:

### Обязательные настройки

* `SECRET_KEY`: Секретный ключ Django для вашего проекта, используемый для криптографической подписи.
   > Пример: `"6l-gr$8+qetg73mu+h1$49$6msube-3gz%&a907y^lakt650e&"`.

* `MAIN_CHANNEL_ID`: Идентификатор основного канала Telegram.
   > Пример: `"100123456789"`.

* `MAIN_CHANNEL_NAME`: Имя основного канала Telegram.
   > Пример: `"ChannelName"`.

* `TELETHON_API_ID`: ID приложения для работы с Telethon, библиотекой Python для работы с API Telegram.
   > Пример: `12345`.

* `TELETHON_API_HASH`: Секретный ключ приложения для работы с Telethon.
   > Пример: `"7d8fd77f6s6"`.

### Настройки разработки (необязательно)

* `DEBUG`: Указывает, должен ли Django использовать режим отладки.
   > Пример: `True` или `False`. По умолчанию `True`. Обратите внимание, что страница регистрации доступна только в режиме отладки (`True`). Для продакшна установите значение `False`.

* `ALLOWED_HOSTS`: Список хостов/доменов, на которых будет работать ваш проект Django. Обязательно добавьте ваш домен в этот список.
   > Пример: `127.0.0.1, 8.8.8.8`. По умолчанию `127.0.0.1`.

### Настройки логирования (необязательно)

* `LOGURU_FOLDER`: Путь до папки для журналов Loguru.
   > Пример: `"my_log_folder/`. По умолчанию `logs`.

* `LOGURU_LEVEL`: Уровень логирования для Loguru.
   > Пример: `"INFO"`. По умолчанию `DEBUG`.

* `LOGURU_FORMAT`: Формат логирования для Loguru.
   > Пример: `"{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"`. По умолчанию этот формат.

### Настройки базы данных (необязательно)

* `DB_ENGINE`: Движок базы данных Django.
   > Пример: `"django.db.backends.mysql"`. По умолчанию используется данный движок.

* `DB_NAME`: Имя вашей базы данных.
   > Пример: `"my_db"`. По умолчанию `cars`.

* `DB_USER`: Имя пользователя для доступа к вашей базе данных.
   > Пример: `"user"`. По умолчанию `root`.

* `DB_PASSWORD`: Пароль для доступа к вашей базе данных.
   > Пример: `"password"`. По умолчанию `root`.

* `DB_HOST`: Хост вашей базы данных.
   > Пример: `"db"`. По умолчанию `localhost`. **Для Docker-контейнера это обязательный параметр, используйте тут `db`.**

* `DB_PORT`: Порт вашей базы данных.
   > Пример: `1234`. По умолчанию `3306`.

### Настройки очереди заданий Celery (необязательно)

* `CELERY_BROKER_URL`: URL брокера для Celery.
   > Пример: `"your-celery-broker-url"`. По умолчанию `redis://localhost:6379`. **Для Docker-контейнера это обязательный параметр, используйте тут `redis://redis:6379`.**

### Настройки Telethon (необязательно)

* `TELETHON_SESSION_NAME`: Имя сессии для Telethon.
   > Пример: `"my_session"`. По умолчанию `session`.

* `TELETHON_SYSTEM_VERSION`: Версия системы для Telethon.
   > Пример: `"4.16.30-vxCUSTOM"`. По умолчанию используется данная версия.

### Другие необязательные настройки

* `LOGIN_URL`: URL для входа в систему.
   > Пример: `"accounts/login/"`. По умолчанию `/users/login/`.

* `ANNOUNCEMENT_LIST_PER_PAGE`: Количество объявлений на странице.
   > Пример: `1`. По умолчанию `5`.

* `TAG_LIST_PER_PAGE`: Количество тегов на странице.
   > Пример: `1`. По умолчанию `10`.

Сохраните и закройте файл.

### Шаг 6: Создание файла сессии Telethon

После заполнения файла конфигурации `.env`, вам необходимо создать файл сессии Telethon для корректной работы сервера с Telegram API. Для этого выполните следующий шаг:

1. Запустите скрипт `create_telethon_session.py`:

   ```bash
   poetry run create_telethon_session.py
   ```

   Скрипт запросит у вас некоторую информацию и автоматически создаст файл сессии Telethon, который будет использоваться вашим приложением.

2. Убедитесь, что файл сессии был создан в правильном месте и имеет корректные права доступа.

Этот шаг необходим для установления соединения с API Telegram и корректной работы вашего сервера.

Понял, извините за недопонимание. В таком случае инструкции должны выглядеть следующим образом:

### Шаг 7: Настройка MySQL

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

Примените миграции:

```bash
cd /var/www/CarWebBot
poetry run python3.11 web/manage.py migrate
```

#### Опционально: Использование файла конфигурации MySQL

В корне проекта есть пример файла `my.cnf`, который можно использовать как отправную точку для настройки MySQL. Если вы хотите использовать эти настройки, выполните следующие шаги:

1. Скопируйте файл `my.cnf` из корня проекта в каталог MySQL:

   ```bash
   sudo cp /var/www/CarWebBot/my.cnf /etc/mysql/my.cnf
   ```

2. Перезапустите службу MySQL, чтобы применить изменения:

   ```bash
   sudo systemctl restart mysql
   ```

Эти настройки предназначены для оптимизации использования памяти и производительности и могут быть дополнительно настроены в зависимости от ваших потребностей.

Не забудьте тестировать систему после применения этих настроек, чтобы убедиться, что все работает корректно.

### Шаг 8: Настройка Redis

Отредактируйте конфигурацию Redis:

```bash
sudo nano /etc/redis/redis.conf
```

Замените строку `supervised no` на `supervised systemd`.

Перезапустите Redis:

```bash
sudo systemctl restart redis.service
```

### Шаг 9: Настройка Gunicorn

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

### Шаг 10: Настройка Nginx

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

### Шаг 11: Настройка Celery и Celery Beat

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

## Автоматизированная установка с Docker

Этот метод позволяет автоматизировать процесс установки, используя Docker и скрипт `initial_setup.bash`. Вам нужно будет только клонировать репозиторий, заполнить файл `.env` и запустить скрипт. Все остальные действия, включая создание сессии Telethon, будут выполнены автоматически.

1. **Подготовка**

      Установите Docker и Docker Compose, используя [эту инструкцию](https://docs.docker.com/engine/install/ubuntu/). Так же установите python версии 3.11  и git:

      ```bash
      sudo apt install software-properties-common -y
      sudo add-apt-repository ppa:deadsnakes/ppa
      sudo apt install python3.11
      sudo apt install git
      ```

2. **Клонирование проекта:**

   ```bash
   git clone https://github.com/SerHappy/CarWebBot.git
   cd CarWebBot
   ```

3. **Настройка файла `.env`:**

   Отредактируйте файл `.env`, следуя инструкциям в [этом разделе](#шаг-5-настройка-переменных-окружения), и сохраните изменения.

   ВНИМАНИЕ: В переменной `ALLOWED_HOSTS` необходимо указать ваш домен и 127.0.0.1, разделенные запятыми.
   `DB_HOST` должен быть `db`, а брокер Celery `CELERY_BROKER_URL` - `redis://redis:6379/0`.

4. **Настройка файла Nginx**

   Отредактируйте файл `CarWebBot.conf`. Замените `your_domain` на ваш домен и сохраните изменения.

5. **Опционально: Настройка файла конфигурации MySQL в Docker**

   Если вы хотите оптимизировать конфигурацию MySQL в контейнере Docker, вы можете настроить предоставленный файл `my.cnf`. Все пути для копирования уже прописаны в docker-compose.yml, поэтому вам нужно будет только отредактировать файл по желанию.

6. **Запуск скрипта установки:**

   ```bash
   chmod +x initial_setup.bash
   ./initial_setup.bash
   ```

   P.S Если при выполнении скрипта вы решили дампить БД, то медиа автоматически не переносится, поэтому вам нужно будет вручную скопировать все содержимое старой директории media и вставить в новую.

7. **Запуск проекта:**
   Если вы не захотели собрать и запускать проект с помощью скрипта, вы можете сделать это вручную:

   ```bash
   docker-compose up -d --build
   ```

Теперь ваш проект должен быть развернут и запущен на вашем сервере. Команды для управления Docker Compose можно найти [здесь](https://docs.docker.com/compose/reference/overview/).
