import logging
from threading import Lock

from telegram import ChatAction

import goglemogle
from user_check import allowed_user

lock = Lock()


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
