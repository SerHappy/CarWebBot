#!/bin/bash

# Checking python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_VERSION_REQUIRED="3.11"
if [ "$(printf '%s\n' "$PYTHON_VERSION" "$PYTHON_VERSION_REQUIRED" | sort -V | head -n1)" == "$PYTHON_VERSION" ]; then
    echo "Python version $PYTHON_VERSION is too old. Please update to $PYTHON_VERSION_REQUIRED or newer."
    exit 1
fi

# Installing virtual environment and Telethon
read -p "Install virtual environment and Telethon? [Y/n] " INSTALL
if [ "$INSTALL" == "Y" ] || [ "$INSTALL" == "y" ]; then
  while true; do
    read -p "Please enter your venv directory (default: .venv): " VENV_DIR
    VENV_DIR=${VENV_DIR:-.venv}

    if [ -d "$VENV_DIR" ]; then
      break
    fi

    read -p "Directory $VENV_DIR does not exist. Create it?[Y/n] " REPLY
    if [ "$REPLY" == "Y" ] || [ "$REPLY" == "y" ]; then
      echo "Creating virtual environment..."
      python3 -m venv $VENV_DIR
      break
    else
      echo "Please enter a valid directory."
    fi
  done

  echo "Activating virtual environment..."
  source $VENV_DIR/bin/activate

  echo "Installing requirements..."
  if ! python3 -m pip install -r requirements.txt; then
    echo "Failed to install requirements. Please check your requirements.txt file."
    exit 1
  fi

  echo "Exporting django settings module..."
  export DJANGO_SETTINGS_MODULE='web.core.settings'

  echo "Creating telethon session..."
  python3 create_session.py

  echo "Quiting virtual environment..."
  deactivate
fi

# Checking docker
if ! docker --version &> /dev/null; then
  echo "Docker is not installed. Please install docker."
  exit 1
fi

# Checking docker-compose
if command -v "docker compose" &> /dev/null
then
    DOCKER_COMPOSE_COMMAND="docker compose"
elif command -v "docker-compose" &> /dev/null
then
    DOCKER_COMPOSE_COMMAND="docker-compose"
else
    echo "Neither 'docker compose' nor 'docker-compose' is available. Please install docker-compose."
    exit 1
fi

echo "Using '$DOCKER_COMPOSE_COMMAND' to manage Docker containers."

# Running docker compose
read -p "Run '$DOCKER_COMPOSE_COMMAND'?[Y/n] " REPLY
if [ "$REPLY" == "Y" ] || [ "$REPLY" == "y" ]; then
  echo "Running '$DOCKER_COMPOSE_COMMAND'..."
  set -e
  $DOCKER_COMPOSE_COMMAND up -d --build
  set +e
  echo "Done! You can check logs with '$DOCKER_COMPOSE_COMMAND logs -f'. \
  Use '$DOCKER_COMPOSE_COMMAND down' to stop the containers."
fi
