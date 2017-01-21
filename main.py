# -*- coding: utf-8 -*-
import logging
from threading import Lock

from telegram import ChatAction
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

import goglemogle
from task import Task

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

allowed_users = ('daniilbubnov', 'julia_vikulina')

todo_list = []

lock = Lock()


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="None of your business!")
        return False
    return True


def add_category(bot, update):
    # TODO implement
    pass


def add(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    logging.info(msg="Adding a task " + str(update.message))

    if not allowed_user(bot, update):
        return

    if update.message.text is None:
        return

    with lock:
        added_task = Task(update.message.text.replace('/add', '').strip())
        todo_list.append(added_task)
        # TODO why are they empty????

        task_str = update.message.text.replace('/add', '').strip().split(",")
        if task_str[0] == '':
            logging.info("Input task is incorrect" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /add Имя задачи[, дата, категория, ссылка]")
            return

        task_name = task_str[0].strip()
        due_date = task_str[1].strip() if len(task_str) > 1 else ""
        category = task_str[2].strip() if len(task_str) > 2 else ""
        link = task_str[3].strip() if len(task_str) > 3 else ""

        result = goglemogle.add_task(task_name, due_date, category, link)
        logging.info(result)
        reply_msg = update.message.from_user.first_name + ", я добавил задачу: " + task_name
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def list_all(bot, update):
    logging.info(msg="Listing tasks ")
    if not allowed_user(bot, update):
        return

    bot.sendMessage(chat_id=update.message.chat_id, text="I have something for you:")
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    values = goglemogle.list_all()
    if not values:
        logging.error(msg="empty response from google sheet")
        bot.sendMessage(chat_id=update.message.chat_id, text="Ups. I cannot find anything.")
    else:
        try:
            # get rid of the title rows
            values = values[3:]
            todo_str = ""
            # append only actual task names
            for row in values:
                if row[0] == "":
                    todo_str += "* " + row[4] + "\n"
            bot.sendMessage(chat_id=update.message.chat_id, text=todo_str)
            logging.info(msg="list of all tasks " + todo_str)

        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e


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


def diary(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    if not allowed_user(bot, update):
        return

    logging.info(msg="Adding a diary record: " + str(update.message))

    with lock:
        text = update.message.text.replace('/diary', '').replace('@DnJTodoBot', '').strip()
        if update.message.text is None:
            bot.sendMessage(chat_id=update.message.chat_id, text="No text provided")
            return
        date = str(update.message.date)
        try:
            result = goglemogle.diary(text, date)
        except Exception as e:
            logging.error(msg="A record was not added")
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        logging.info(result)
        reply_msg = update.message.from_user.first_name + ", я добавил твой пост от " + date
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def money(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    if not allowed_user(bot, update):
        return

    logging.info(msg="Adding a money record: " + str(update.message.text))

    with lock:
        task_str = update.message.text.replace('/money', '').replace('@DnJTodoBot', '').strip().split(',')
        if update.message.text is None:
            bot.sendMessage(chat_id=update.message.chat_id, text="No text provided")
            return

        amount = task_str[0].strip()
        if amount is "":
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /money сумма [, цель, категория, дата]."
                                                                 "\nПример: /money 100, котята, Подарки, 05.03")
            return
        expense_name = task_str[1].strip() if len(task_str) > 1 else ""
        category = task_str[2].strip() if len(task_str) > 2 else ""
        date = task_str[3].strip() if len(task_str) > 3 else str(update.message.date.date())

        try:
            result = goglemogle.money(expense_name, amount, category, date)
        except Exception as e:
            logging.error(msg="A record was not added")
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        logging.info(result)
        reply_msg = update.message.from_user.first_name + ", я добавил расход: " + expense_name
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def current_weather(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    if not allowed_user(bot, update):
        return

    logging.info(msg="Finding out current weather... ")
    link = "http://api.openweathermap.org/data/2.5/weather?lat=59.95&lon=30.21&appid=d9022c300d4c076fd764ce33996e75ac"
    import requests

    resp = requests.get(link)
    if resp.status_code != 200:
        # This means something went wrong.
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(resp.status_code))
        raise EnvironmentError('GET /weather?lat=59.95&lon=30.21 {}'.format(resp.status_code))

    logging.info(resp.json())
    reply_msg = update.message.from_user.first_name + ", погода в СПб " + str(resp.json())
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


updater = Updater(token='TOKEN')

start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)
add_handler = CommandHandler('add', add)
updater.dispatcher.add_handler(add_handler)

listall_handler = CommandHandler('listall', list_all)
updater.dispatcher.add_handler(listall_handler)

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
