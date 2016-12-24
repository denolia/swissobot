# -*- coding: utf-8 -*-
import logging
from threading import Lock

from telegram.ext import CommandHandler
from telegram.ext import Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# TODO /stop command
# TODO authorization

allowed_users = ('daniilbubnov', 'julia_vikulina')

todo_list = []

lock = Lock()


def stop(bot, update):
    # TODO implement stop
    pass


def add(bot, update):
    logging.log(level=logging.INFO, msg="Adding a task " + str(update.message))
    if not allowed_user(bot, update):
        return
    if update.message.text is None:
        return
    with lock:
        todo_list.append(update.message.text)
    pass


def listall(bot, update):
    logging.log(level=logging.INFO, msg="Listing tasks ")
    if not allowed_user(bot, update):
        return
    bot.sendMessage(chat_id=update.message.chat_id, text=todo_list)
    pass


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="None of your business!")
        return False
    return True


def start(bot, update):
    logging.log(level=logging.INFO, msg="received message" + str(update))

    if not allowed_user(bot, update):
        return
    bot.sendMessage(chat_id=update.message.chat_id, text="Hola!")


updater = Updater(token='TOKEN')
add_handler = CommandHandler('add', add)
listall_handler = CommandHandler('listall', listall)

updater.dispatcher.add_handler(add_handler)
updater.dispatcher.add_handler(listall_handler)

updater.start_polling()  # поехали!
