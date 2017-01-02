# -*- coding: utf-8 -*-
import logging
from threading import Lock

from telegram.ext import CommandHandler
from telegram.ext import Updater

import goglemogle
from task import Task

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
# TODO /stop command
# TODO authorization

allowed_users = ('daniilbubnov', 'julia_vikulina')

todo_list = []

lock = Lock()


def add_category(bot, update):
    # TODO implement
    pass


def add(bot, update):
    logging.debug(msg="Adding a task " + str(update.message))
    if not allowed_user(bot, update):
        return

    if update.message.text is None:
        return

    with lock:
        added_task = Task(update.message.text.replace('/add', '').strip())
        todo_list.append(added_task)

        task_str = update.message.text.replace('/add', '').strip().split(",")
        if task_str[0] == '':
            logging.debug("Input task is incorrect" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /add Имя задачи[, дата, категория, ссылка]")
            return

        task_name = task_str[0].strip()
        due_date = task_str[1].strip() if len(task_str) > 1 else ""
        category = task_str[2].strip() if len(task_str) > 2 else "Дела"
        link = task_str[3].strip() if len(task_str) > 3 else ""

        result = goglemogle.add_task(task_name, due_date, category, link)
        logging.debug("Task is successfully added: " + str(added_task))
        logging.debug(result)
        bot.sendMessage(chat_id=update.message.chat_id, text="Добавлено: " + task_name)


def list_all(bot, update):
    logging.debug(msg="Listing tasks ")
    if not allowed_user(bot, update):
        return
    bot.sendMessage(chat_id=update.message.chat_id, text=str(todo_list))


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="None of your business!")
        return False
    return True


updater = Updater(token='TOKEN')
add_handler = CommandHandler('add', add)
listall_handler = CommandHandler('listall', list_all)

updater.dispatcher.add_handler(add_handler)
updater.dispatcher.add_handler(listall_handler)

updater.start_polling()  # поехали!
