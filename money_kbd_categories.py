import datetime
import logging
from threading import Lock
from dateutil.parser import parse

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


def money_handler(bot, update):
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

    reply_markup = compose_categories_kbd(user_group)

    update.message.reply_text('Please choose category:', reply_markup=reply_markup)


def compose_categories_kbd(user_group):
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
    return reply_markup


def money_list_handler(bot, update):
    logging.info(msg="Getting list of expenses for a date: " + str(update.message.text))
    user_group = check_user_type(bot, update)
    if user_group != "d&j":
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    if update.message.text is None:
        bot.sendMessage(chat_id=update.message.chat_id, text="No text provided")
        return

    task_str = update.message.text.replace('/moneylist', '').replace('@DnJTodoBot', '').strip().split(';')

    date = parse(task_str[0].strip()).date()
    if date is "":
        date = update.message.date.date()

    try:
        values = goglemogle.money_list(user_group)
    except Exception as e:
        logging.error(e)
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
        raise e

    if not values:
        logging.error(msg="empty response from google sheet")
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Oops. I cannot find anything.")
    else:
        try:
            print_money_list(bot, update, values, date)

        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e
            # go to google spreadsheet
            # obtain full list of expenses
            # choose only those with the requested date
            # send a message


def print_money_list(bot, update, values, date: datetime.date):

    money_str = ""
    expense_number = 0
    row_found_flag = False

    row_address = 1     # to start from 2
    for row in values:
        row_address += 1
        expense_date = parse(row[0]).date()
        if expense_date == date:
            row_found_flag = True
            expense_number += 1
            money_str += "[{row}] {date}; {cat}; {value}; {aim}\n".format(row=row_address,
                                                                        date=row[0],
                                                                        cat=row[1],
                                                                        value=row[2],
                                                                        aim=row[3])
            # print by chunks of 10 tasks
            if expense_number >= 10:
                bot.sendMessage(chat_id=update.message.chat_id, text=money_str)
                logging.info(msg="list of expenses " + money_str)
                expense_number = 0
                money_str = ""

    # print the rest part
    if money_str != "":
        bot.sendMessage(chat_id=update.message.chat_id, text=money_str)
        logging.info(msg="list of expenses " + money_str)

    if not row_found_flag:
        bot.sendMessage(chat_id=update.message.chat_id, text="Nothing was found for date: {date}".format(date=date))
        logging.info(msg="list of expenses " + money_str)


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
