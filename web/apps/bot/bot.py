from decouple import config
from telebot import TeleBot


# Инициализируем бота
bot: TeleBot = TeleBot(config("TELEGRAM_BOT_TOKEN", cast=str))  # type: ignore
