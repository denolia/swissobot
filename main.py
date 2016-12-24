# -*- coding: utf-8 -*-
import logging
from threading import Lock

from telegram.ext import CommandHandler
from telegram.ext import Updater

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
        added_task = Task(update.message.text.replace('/add ', ''))
        todo_list.append(added_task)
        logging.debug("Task is successfully added: " + str(added_task))
    pass


def listall(bot, update):
    logging.debug(msg="Listing tasks ")
    if not allowed_user(bot, update):
        return
    bot.sendMessage(chat_id=update.message.chat_id, text=str(todo_list))
    pass


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="None of your business!")
        return False
    return True


updater = Updater(token='TOKEN')
add_handler = CommandHandler('add', add)
listall_handler = CommandHandler('listall', listall)

updater.dispatcher.add_handler(add_handler)
updater.dispatcher.add_handler(listall_handler)

updater.start_polling()  # поехали!
