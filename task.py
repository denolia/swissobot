import logging
from threading import Lock

from telegram import ChatAction

import goglemogle
from user_check import check_user_type


def add_category(bot, update):
    # TODO implement
    pass


lock = Lock()


def task(bot, update):
    logging.info(msg="Adding a task " + str(update.message))

    user_group = check_user_type(bot, update)
    if user_group is None or user_group == "":
        return

    if update.message.text is None:
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    with lock:
        task_str = update.message.text \
            .replace('/task', '') \
            .replace('@DnJTodoBot', '') \
            .strip() \
            .split(";")
        if task_str[0] == '':
            logging.info("Input task is empty" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /task Имя задачи [; категория; дата; ссылка]")
            return

        task_name = task_str[0].strip()
        category = task_str[1].strip() if len(task_str) > 1 else ""
        due_date = task_str[2].strip() if len(task_str) > 2 else ""
        link = task_str[3].strip() if len(task_str) > 3 else ""

        try:
            result = goglemogle.add_task(user_group, task_name, due_date, category, link)
        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        logging.info(result)
        reply_msg = update.message.from_user.first_name + ", я добавил задачу: " + task_name
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def task_list(bot, update):
    logging.info(msg="Listing tasks ")

    user_group = check_user_type(bot, update)
    if user_group != "d&j":
        return

    bot.sendMessage(chat_id=update.message.chat_id, text="I have something for you:")

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    try:
        values = goglemogle.task_list(user_group)
    except Exception as e:
        logging.error(e)
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
        raise e

    if not values:
        logging.error(msg="empty response from google sheet")
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Oops. I cannot find anything. \nHave you finished everything? Amazing!")
    else:
        try:
            print_task_list(bot, update, values)

        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e


def print_task_list(bot, update, values):
    # get rid of the title rows
    values = values[3:]
    todo_str = ""
    task_number = 0
    # append only actual task names
    for row in values:
        if row[0] == "":
            task_number += 1
            todo_str += "[" + row[5] + "] " + row[4] + "\n"
            # print by chunks of 10 tasks
            if task_number >= 10:
                bot.sendMessage(chat_id=update.message.chat_id, text=todo_str)
                logging.info(msg="list of tasks " + todo_str)
                task_number = 0
                todo_str = ""

    # print the rest part
    if todo_str != "":
        bot.sendMessage(chat_id=update.message.chat_id, text=todo_str)
        logging.info(msg="list of tasks " + todo_str)


def done_task(bot, update):
    logging.info(msg="Finishing a task " + str(update.message))

    user_group = check_user_type(bot, update)
    if user_group is None or user_group == "":
        return

    if update.message.text is None:
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    with lock:
        task_str = update.message.text \
            .replace('/done', '') \
            .replace('@DnJTodoBot', '') \
            .strip()
        if task_str == '':
            logging.info("String with task id is empty" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /done id")
            return

        try:
            task_id = int(task_str)
            result = goglemogle.finish_task(user_group, task_id)
        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        if result is False:
            logging.info(result)
            reply_msg = update.message.from_user.first_name + ", эта задача уже была завершена"
            bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
        else:
            logging.info(result)
            reply_msg = update.message.from_user.first_name + ", я завершил задачу " + str(task_id)
            bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
