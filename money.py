import logging
from threading import Lock

from telegram import ChatAction

import goglemogle
from user_check import allowed_user

lock = Lock()


def money(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    # TODO return user type
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
