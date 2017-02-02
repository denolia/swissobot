
import logging
from threading import Lock

from telegram import ChatAction
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import goglemogle
from goglemogle import get_categories
from user_check import check_user_type, get_user_group
from math import ceil

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

CATEGORIES = {}
lock = Lock()

EXPENSE = {}


def money(bot, update):
    logging.info(msg="Adding a money record: " + str(update.message.text))
    user_group = check_user_type(bot, update)
    if user_group != "d&j":
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    with lock:
        task_str = update.message.text.replace('/money', '').replace('@DnJTodoBot', '').strip().split(';')
        if update.message.text is None:
            bot.sendMessage(chat_id=update.message.chat_id, text="No text provided")
            return

        amount = task_str[0].strip()
        if amount is "":
            bot.sendMessage(chat_id=update.message.chat_id, text="Формат: /money сумма [; цель; дата]."
                                                                 "\nПример: /money 100; котята; Подарки; 05.03")
            return
        expense_name = task_str[1].strip() if len(task_str) > 1 else ""
        date = task_str[2].strip() if len(task_str) > 2 else str(update.message.date.date())

        global EXPENSE
        EXPENSE.update({update.message.from_user.username: [amount, expense_name, date]})

    cat = CATEGORIES.get(user_group)
    if cat is None:
        cat = get_categories(user_group)
        CATEGORIES.update({user_group: cat})

    cat_num = len(cat)
    cat_rows = ceil(cat_num / 3)
    keyboard = []
    for row_num in range(cat_rows):
        row = []
        for col_num in range(3):
            cat_index = 3 * row_num + col_num
            row.append(InlineKeyboardButton(cat[cat_index], callback_data=str(cat_index)))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose category:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query
    user = query.from_user.username
    user_group = get_user_group(user)
    if user_group == "":
        return

    category = CATEGORIES.get(user_group)[int(query.data)]

    bot.editMessageText(text="Выбрана категория: {}".format(category),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

    expense_data = EXPENSE.get(user)
    amount = expense_data[0]
    expense_name = expense_data[1]
    date = expense_data[2]

    try:
        result = goglemogle.money(user_group, expense_name, amount, category, date)
    except Exception as e:
        logging.error(msg="A record was not added")
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
        raise e

    logging.info(result)
    reply_msg = "{}, я добавил расход: {}; {}; {}; {}".format(query.from_user.first_name,
                                                              amount,
                                                              expense_name,
                                                              category,
                                                              date)

    bot.sendMessage(chat_id=update.callback_query.message.chat_id, text=reply_msg)


def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

