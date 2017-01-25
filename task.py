import logging
from threading import Lock

from telegram import ChatAction

import goglemogle
from user_check import allowed_user


def add_category(bot, update):
    # TODO implement
    pass


lock = Lock()


def add(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    logging.info(msg="Adding a task " + str(update.message))

    if not allowed_user(bot, update):
        return

    if update.message.text is None:
        return

    with lock:
        task_str = update.message.text \
            .replace('/add', '') \
            .replace('@DnJTodoBot', '') \
            .strip() \
            .split(",")
        if task_str[0] == '':
            logging.info("Input task is empty" + str(update.message.text))
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


def task_list(bot, update):
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
