# coding=utf-8

import logging
from threading import Lock

from telegram import ChatAction

from googlesheets import goglemogle
from utils.commands import get_operands, DIARY_COMMAND, handle_error
from utils.user_check import get_user_group

lock = Lock()

log = logging.getLogger(__name__)


def diary_handler(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, DIARY_COMMAND, "Sorry, you are not allowed to write to the diary")
        return

    log.info(msg="Adding a diary record: " + str(update.message))

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
            goglemogle.diary(text, date)
    except Exception as e:
        handle_error(bot, update, DIARY_COMMAND, str(e))
        raise e

    reply_msg = update.message.from_user.first_name + ", я добавил твой пост от " + date
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
