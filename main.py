# coding=utf-8

import logging

from telegram import ChatAction
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from commands import MONEY_COMMAND, MONEY_EDIT_COMMAND, TASK_DELETE_COMMAND, MONEY_LIST_COMMAND, DIARY_COMMAND
from diary import diary_handler
from money import money_handler, money_callback_handler, money_list_handler, money_edit_handler
from task import task, task_list, done_task, task_delete_handler
from weather import current_weather

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

help_text = """
Доступные команды:
{money_format}
{money_list_format} - список расходов за дату с id
{money_edit_format} - изменить запись о расходе по id

{diary_format} запись
/task Имя задачи [; категория; дата; ссылка]
/tasklist - показать список всех актуальных задач
{task_delete_format}
/weather - показать погоду


Примеры:
{money_example}
{diary_example}
/task Погладить котика; Дела; 21.01; google.com
""".format(money_format=MONEY_COMMAND.format,
           money_list_format=MONEY_LIST_COMMAND.format,
           money_example=MONEY_COMMAND.example,
           task_delete_format=TASK_DELETE_COMMAND.format,
           money_edit_format=MONEY_EDIT_COMMAND.format,
           diary_format=DIARY_COMMAND.format,
           diary_example=DIARY_COMMAND.example
           )


def start(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Hi, guys! Welcome to the awesome multifunctional bot!\n" + help_text)


def bot_help(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=help_text)


def unknown(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Sorry, I didn't understand that command.")


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


updater = Updater(token='TOKEN')

updater.dispatcher.add_handler( CommandHandler('start', start))
updater.dispatcher.add_handler( CommandHandler('task', task)
)

updater.dispatcher.add_handler(CommandHandler('tasklist', task_list))

updater.dispatcher.add_handler(CommandHandler(TASK_DELETE_COMMAND.name, task_delete_handler))

updater.dispatcher.add_handler(CommandHandler('done', done_task))

updater.dispatcher.add_handler(CommandHandler(DIARY_COMMAND.name, diary_handler))

updater.dispatcher.add_handler(CommandHandler(MONEY_COMMAND.name, money_handler))

updater.dispatcher.add_handler(CommandHandler(MONEY_LIST_COMMAND.name, money_list_handler))

updater.dispatcher.add_handler(CommandHandler(MONEY_EDIT_COMMAND.name, money_edit_handler))

updater.dispatcher.add_handler(CallbackQueryHandler(money_callback_handler))

updater.dispatcher.add_handler(CommandHandler('weather', current_weather))

updater.dispatcher.add_handler(CommandHandler('help', bot_help))

updater.dispatcher.add_error_handler(error)

# Note: must be the last added to handler
updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Start the Bot
updater.start_polling()

# Run the bot until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT
updater.idle()
