#!/bin/bash

declare -A messages

# English
messages["en_prompt_python"]="Python 3.11 or newer is not installed. Please install Python 3.11 or newer."
messages["en_using_python"]="Using Python%s"
messages["en_prompt_install"]="Install virtual environment and Telethon? [Y/n] "
messages["en_prompt_venv"]="Please enter your venv directory (default: .venv): "
messages["en_dir_not_exist"]="Directory does not exist. Create it? [Y/n] "
messages["en_dir_creating"]="Creating virtual environment..."
messages["en_dir_invalid"]="Please enter a valid directory."
messages["en_venv_activate"]="Activating virtual environment..."
messages["en_venv_requirements"]="Installing requirements..."
messages["en_venv_failed"]="Failed to install requirements. Please check your requirements.txt file."
messages["en_export_django_settings"]="Exporting django settings module..."
messages["en_create_telethon_session"]="Creating telethon session..."
messages["en_venv_quit"]="Quiting virtual environment..."
messages["en_docker_not_installed"]="Docker is not installed. Please install docker."
messages["en_docker_compose_not_installed"]="Neither 'docker compose' nor 'docker-compose' is available. Please install docker-compose."
messages["en_prompt_dump_db"]="Do you want to dump your current database and import it into Docker? [Y/n] "
messages["en_prompt_db_user"]="Please enter your database username: "
messages["en_prompt_db_pass"]="Please enter your database password: "
messages["en_prompt_db_name"]="Please enter your database name: "
messages["en_invalid_credentials"]="Invalid credentials or database name. Please try again."
messages["en_dumping_db"]="Dumping database..."
messages["en_db_dumped"]="Database dumped successfully."
messages["en_db_coping"]="Copying the dump file into the Docker container..."
messages["en_db_copied"]="Dump file copied successfully."
messages["en_db_importing"]="Importing the dump file into the Docker container..."
messages["en_db_imported"]="Dump file imported successfully."
messages["en_dump_removing"]="Removing the dump file..."
messages["en_dump_removed"]="Dump file removed successfully."

# Russian
messages["ru_prompt_python"]="Python 3.11 или новее не установлен. Пожалуйста, установите Python 3.11 или новее."
messages["ru_using_python"]="Используется Python%s"
messages["ru_prompt_install"]="Установить виртуальное окружение и Telethon? [Y/n] "
messages["ru_prompt_venv"]="Пожалуйста, введите директорию для venv (по умолчанию: .venv): "
messages["ru_dir_not_exist"]="Директория не существует. Создать её? [Y/n] "
messages["ru_dir_creating"]="Создание виртуального окружения..."
messages["ru_dir_invalid"]="Пожалуйста, введите действительную директорию."
messages["ru_venv_activate"]="Активация виртуального окружения..."
messages["ru_venv_requirements"]="Установка зависимостей..."
messages["ru_venv_failed"]="Не удалось установить зависимости. Пожалуйста, проверьте ваш requirements.txt файл."
messages["ru_export_django_settings"]="Экспорт django settings module..."
messages["ru_create_telethon_session"]="Создание telethon сессии..."
messages["ru_venv_quit"]="Выход из виртуального окружения..."
messages["ru_docker_not_installed"]="Docker не установлен. Пожалуйста, установите docker."
messages["ru_docker_compose_not_installed"]="Ни 'docker compose', ни 'docker-compose' не доступны. Пожалуйста, установите docker-compose."
messages["ru_prompt_dump_db"]="Вы хотите выгрузить текущую базу данных и импортировать её в Docker? [Y/n] "
messages["ru_prompt_db_user"]="Пожалуйста, введите имя пользователя базы данных: "
messages["ru_prompt_db_pass"]="Пожалуйста, введите пароль базы данных: "
messages["ru_prompt_db_name"]="Пожалуйста, введите имя базы данных: "
messages["ru_invalid_credentials"]="Неверные учетные данные или имя базы данных. Пожалуйста, попробуйте еще раз."
messages["ru_dumping_db"]="Выгрузка базы данных..."
messages["ru_db_dumped"]="База данных успешно выгружена."
messages["ru_db_coping"]="Копирование файла дампа в контейнер Docker..."
messages["ru_db_copied"]="Файл дампа успешно скопирован."
messages["ru_db_importing"]="Импортирование файла дампа в контейнер Docker..."
messages["ru_db_imported"]="Файл дампа успешно импортирован."
messages["ru_dump_removing"]="Удаление файла дампа..."
messages["ru_dump_removed"]="Файл дампа успешно удален."

LANG="en"

get_message() {
  key="$LANG"_"$1"
  shift
  printf "${messages[$key]}" "$@"
}

echo "Choose your language:"
echo "1. English"
echo "2. Русский"
read -p "Enter your choice: [1/2] " CHOICE
if [ "$CHOICE" == "2" ]; then
  LANG="ru"
fi

# Checking python version
PYTHON_CMD="python3.11"
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "$(get_message "prompt_python")"
    exit 1
fi

# Now use $PYTHON_CMD instead of `python3`
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "$(get_message "using_python") $PYTHON_VERSION"

# Installing virtual environment and Telethon
read -p "$(get_message "prompt_install")" INSTALL
if [ "$INSTALL" == "Y" ] || [ "$INSTALL" == "y" ]; then
  while true; do
    read -p "$(get_message "prompt_venv")" VENV_DIR
    VENV_DIR=${VENV_DIR:-.venv}

    if [ -d "$VENV_DIR" ]; then
      break
    fi

    read -p "$(get_message "dir_not_exist")" REPLY
    if [ "$REPLY" == "Y" ] || [ "$REPLY" == "y" ]; then
      echo "$(get_message "dir_creating")"
      $PYTHON_CMD -m venv $VENV_DIR
      break
    else
      echo "$(get_message "dir_invalid")"
    fi
  done

  echo "$(get_message "venv_activate")"
  source $VENV_DIR/bin/activate

  echo "$(get_message "venv_requirements")"
  if ! $PYTHON_CMD -m pip install -r requirements.txt; then
    echo "$(get_message "venv_failed")"
    exit 1
  fi

  echo "$(get_message "export_django_settings")"
  export DJANGO_SETTINGS_MODULE='web.core.settings'

  echo "$(get_message "create_telethon_session")"
  set -e
  $PYTHON_CMD create_telethon_session.py
  set +e

  echo "$(get_message "venv_quit")"
  deactivate
fi

# Checking docker
if ! docker --version &> /dev/null; then
  echo "$(get_message "docker_not_installed")"
  exit 1
fi

# Checking docker-compose
DOCKER_COMPOSE_COMMAND=""

if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE_COMMAND="docker compose"
    elif docker-compose version &> /dev/null; then
        DOCKER_COMPOSE_COMMAND="docker-compose"
    fi
fi

if [ -z "$DOCKER_COMPOSE_COMMAND" ]; then
    echo "$(get_message "docker_compose_not_installed")"
    exit 1
fi

# English translation for docker-compose
messages["en_prompt_docker"]="Run '$DOCKER_COMPOSE_COMMAND'? [Y/n] "
messages["en_using_docker_compose"]="Using '$DOCKER_COMPOSE_COMMAND' to manage Docker containers."
messages["en_docker_compose_running"]="Running '$DOCKER_COMPOSE_COMMAND'..."
messages["en_docker_compose_done"]="Done! You can check logs with '$DOCKER_COMPOSE_COMMAND logs -f'. \
  Use '$DOCKER_COMPOSE_COMMAND down' to stop the containers."
messages["en_prompt_docker"]="Run '$DOCKER_COMPOSE_COMMAND'? [Y/n] "

# Russian translation for docker-compose
messages["ru_prompt_docker"]="Запустить '$DOCKER_COMPOSE_COMMAND'? [Y/n] "
messages["ru_using_docker_compose"]="Используется '$DOCKER_COMPOSE_COMMAND' для управления Docker контейнерами."
messages["ru_docker_compose_running"]="Запуск '$DOCKER_COMPOSE_COMMAND'..."
messages["ru_docker_compose_done"]="Готово! Вы можете проверить логи с помощью '$DOCKER_COMPOSE_COMMAND logs -f'. \
  Используйте '$DOCKER_COMPOSE_COMMAND down' для остановки контейнеров."
messages["ru_prompt_docker"]="Запустить '$DOCKER_COMPOSE_COMMAND'? [Y/n] "

echo "$(get_message "using_docker_compose")"

# Running docker compose
read -p "$(get_message "prompt_docker")" REPLY
if [ "$REPLY" == "Y" ] || [ "$REPLY" == "y" ]; then
  # Running server
  echo "$(get_message "docker_compose_running")"
  set -e
  $DOCKER_COMPOSE_COMMAND up -d --build
  set +e
  echo "$(get_message "docker_compose_done")"

  # Dumping database
  read -p "$(get_message "prompt_dump_db")" DUMP_DB
  if [ "$DUMP_DB" == "Y" ] || [ "$DUMP_DB" == "y" ]; then
   while true; do
      # Enter database credentials
      read -p "$(get_message "prompt_db_user")" DB_USER
      read -s -p "$(get_message "prompt_db_pass")" DB_PASSWORD
      echo
      read -p "$(get_message "prompt_db_name")" DB_NAME

      # Check if the credentials are valid
      if mysql -u $DB_USER -p$DB_PASSWORD -e "USE $DB_NAME" &>/dev/null; then
        break
      else
        echo "$(get_message "invalid_credentials")"
      fi
    done

    # Dumping database
    echo "$(get_message "dumping_db")"
    set -e
    mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > mydatabase.sql
    set +e
    echo "$(get_message "db_dumped")"

    # Copying the dump file into the Docker container
    echo "$(get_message "db_coping")"
    set -e
    $DOCKER_COMPOSE_COMMAND cp mydatabase.sql db:/mydatabase.sql
    set +e
    echo "$(get_message "db_copied")"

    # Importing the dump into the Docker DB
    echo "$(get_message "db_importing")"
    set -e
    $DOCKER_COMPOSE_COMMAND exec db bash -c "mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME < mydatabase.sql"
    set +e
    echo "$(get_message "db_imported")"

    # Removing the dump file
    echo "$(get_message "dump_removing")"
    set -e
    rm mydatabase.sql
    set +e
    echo "$(get_message "dump_removed")"
  fi
fi
