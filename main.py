# -*- coding: utf-8 -*-
import logging

from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from diary import diary
from money import money
from task import add, task_list
from weather import current_weather

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

help_text = """
Привет! Я понимаю следующие команды:
/money сумма [, цель, категория, дата]
/diary запись
/task задача [, ]

Пример: /money 100, котята, Подарки, 05.03
"""


def start(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Hi, guys! What's up?")


def bot_help(bot, update):

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Ну вы держитесь там")


def unknown(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


updater = Updater(token='TOKEN')

start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)
add_handler = CommandHandler('task', add)
updater.dispatcher.add_handler(add_handler)

tasklist_handler = CommandHandler('tasklist', task_list)
updater.dispatcher.add_handler(tasklist_handler)

diary_handler = CommandHandler('diary', diary)
updater.dispatcher.add_handler(diary_handler)

money_handler = CommandHandler('money', money)
updater.dispatcher.add_handler(money_handler)

weather_handler = CommandHandler('weather', current_weather)
updater.dispatcher.add_handler(weather_handler)

help_handler = CommandHandler('help', bot_help)
updater.dispatcher.add_handler(help_handler)

# Note: must be the last added to handler
unknown_handler = MessageHandler(Filters.command, unknown)
updater.dispatcher.add_handler(unknown_handler)

updater.start_polling()  # поехали!
