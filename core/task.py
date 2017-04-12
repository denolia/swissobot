# coding=utf-8

import logging
from threading import Lock

from telegram import ChatAction

from googlesheets import goglemogle
from utils.commands import TASK_DELETE_COMMAND, handle_error, get_operands
from utils.user_check import get_user_group

lock = Lock()

log = logging.getLogger(__name__)


def task(bot, update):
    log.info(msg="Adding a task " + str(update.message))

    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, None, "Access denied")
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
            log.info("Input task is empty" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /task Имя задачи [; категория; дата; ссылка]")
            return

        task_name = task_str[0].strip()
        category = task_str[1].strip() if len(task_str) > 1 else ""
        due_date = task_str[2].strip() if len(task_str) > 2 else ""
        link = task_str[3].strip() if len(task_str) > 3 else ""

        try:
            result = goglemogle.add_task(user_group, task_name, due_date, category, link)
        except Exception as e:
            log.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        log.info(result)
        reply_msg = update.message.from_user.first_name + ", я добавил задачу: " + task_name
        bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def task_list(bot, update):
    log.info(msg="Listing tasks ")

    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, None, "Access denied")
        return

    bot.sendMessage(chat_id=update.message.chat_id, text="I have something for you:")

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    try:
        values = goglemogle.task_list(user_group)
    except Exception as e:
        log.error(e)
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
        raise e

    if not values:
        log.error(msg="empty response from google sheet")
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Oops. I cannot find anything. \nHave you finished everything? Amazing!")
    else:
        try:
            print_task_list(bot, update, values)

        except Exception as e:
            log.error(e)
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
                log.info(msg="list of tasks " + todo_str)
                task_number = 0
                todo_str = ""

    # print the rest part
    if todo_str != "":
        bot.sendMessage(chat_id=update.message.chat_id, text=todo_str)
        log.info(msg="list of tasks " + todo_str)


def done_task(bot, update):
    log.info(msg="Finishing a task " + str(update.message))

    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, None, "Access denied")
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    with lock:
        task_str = update.message.text \
            .replace('/done', '') \
            .replace('@DnJTodoBot', '') \
            .strip()
        if task_str == '':
            log.info("String with task id is empty" + str(update.message.text))
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /done id")
            return

        # TODO check what if it is not int

        try:
            task_id = int(task_str)
            result = goglemogle.finish_task(user_group, task_id)
        except Exception as e:
            log.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e

        if result is False:
            log.info(result)
            reply_msg = update.message.from_user.first_name + ", эта задача уже была завершена"
            bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
        else:
            log.info(result)
            reply_msg = update.message.from_user.first_name + ", я завершил задачу " + str(task_id)
            bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def task_delete_handler(bot, update):
    log.info(msg="Deleting a task " + str(update.message))

    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, None, "Access denied")
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    try:
        operands = get_operands(TASK_DELETE_COMMAND, update.message.text)
    except Exception as e:
        handle_error(bot, update, TASK_DELETE_COMMAND, str(e))
        raise e

    if operands[0] is not None:
        task_id = operands[0]
    else:
        handle_error(bot, update, TASK_DELETE_COMMAND, "No task id provided")
        return

    try:
        task_id = int(task_id)
        with lock:
            result = goglemogle.delete_task(user_group, task_id)
    except Exception as e:
        handle_error(bot, update, TASK_DELETE_COMMAND, str(e))
        raise e

    log.info(result)
    reply_msg = update.message.from_user.first_name + ", я удалил задачу " + str(task_id)
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
