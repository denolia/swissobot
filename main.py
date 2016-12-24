# -*- coding: utf-8 -*-
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging

# TODO /stop command
# TODO authorization

allowed_users = ('daniilbubnov', 'julia_vikulina')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def stop(bot, update):
    # TODO implement stop
    pass


def start(bot, update):
    logging.log(level=logging.INFO, msg="received message" + str(update))

    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="None of your business!")
        return
    bot.sendMessage(chat_id=update.message.chat_id, text="Hola!")


updater = Updater(token='TOKEN')
start_handler = CommandHandler('start', start)
stop_handler = CommandHandler('stop', stop)

updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(stop_handler)

updater.start_polling()  # поехали!
