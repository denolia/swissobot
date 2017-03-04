# coding=utf-8

import logging
from threading import Lock

from telegram import ChatAction

import goglemogle
from commands import get_operands, DIARY_COMMAND, handle_error
from user_check import check_user_type

lock = Lock()


def diary_handler(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    user_group = check_user_type(bot, update)
    if user_group != "d&j":
        return

    logging.info(msg="Adding a diary record: " + str(update.message))

    try:
        operands = get_operands(DIARY_COMMAND, update.message.text)
    except Exception as e:
        handle_error(bot, update, DIARY_COMMAND, str(e))
        raise e

    text = operands[0]
    if text is None:
        handle_error(bot, update, DIARY_COMMAND)
        return

    date = str(update.message.date)

    try:
        with lock:
            result = goglemogle.diary(text, date)
    except Exception as e:
        handle_error(bot, update, DIARY_COMMAND, str(e))
        raise e

    reply_msg = update.message.from_user.first_name + ", я добавил твой пост от " + date
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
