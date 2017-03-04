# coding=utf-8

import datetime
import logging
from math import ceil
from threading import Lock

from dateutil.parser import parse
from telegram import ChatAction
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import goglemogle
from commands import get_operands, handle_error, MONEY_LIST_COMMAND, MONEY_COMMAND, MONEY_EDIT_COMMAND
from goglemogle import get_categories
from user_check import check_user_type, get_user_group

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

    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)

    try:
        operands = get_operands(MONEY_COMMAND, update.message.text)
    except Exception as e:
        handle_error(bot, update, MONEY_COMMAND, str(e))
        raise e

    amount = operands[0]
    if amount is None:
        handle_error(bot, update, MONEY_COMMAND)
        return

    if operands[1] is not None:
        expense_name = operands[1]
    else:
        expense_name = ""

    if operands[2] is not None:
        date = operands[2]
    else:
        date = str(update.message.date.date())

    try:
        parse(date).date()
    except Exception as e:
        handle_error(bot, update, MONEY_COMMAND, str(e))
        return

    with lock:
        global EXPENSE
        # TODO a key shall be a message id, not a username
        EXPENSE[update.message.from_user.username] = [amount, expense_name, date]

    reply_markup = compose_categories_kbd(user_group)
    update.message.reply_text('Please choose category:', reply_markup=reply_markup)


def money_callback_handler(bot, update):
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
    if expense_data is not None:
        amount = expense_data[0]
        expense_name = expense_data[1]
        date = expense_data[2]
    else:
        logging.error(msg="No records found for user {user}, current records: {map}"
                          "".format(user=user, map=EXPENSE))
        msg = "Wrong user has clicked on the keyboard, please repeat entering money record"
        bot.editMessageText(chat_id=query.message.chat_id,
                            text=msg,
                            message_id=query.message.message_id)
        return

    try:
        result = goglemogle.money(user_group, expense_name, amount, category, date)
        upd_range = result.split('!')[-1]
    except Exception as e:
        logging.error(msg="A record was not added")
        bot.editMessageText(chat_id=query.message.chat_id,
                            text="Sorry,\n" + str(e),
                            message_id=query.message.message_id)
        raise e

    logging.info("Changed range {}".format(upd_range))
    reply_msg = "{name}, я добавил расход: " \
                "{amount}; {expense_name}; {category}; {date}\n" \
                "Updated range: {range}" \
                "".format(name=query.from_user.first_name,
                          amount=amount,
                          expense_name=expense_name,
                          category=category,
                          date=date,
                          range=upd_range)

    bot.editMessageText(chat_id=update.callback_query.message.chat_id,
                        text=reply_msg,
                        message_id=query.message.message_id)


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
        handle_error(bot, update, MONEY_LIST_COMMAND, 'No text provided')
        return

    try:
        operands = get_operands(MONEY_LIST_COMMAND, update.message.text)
    except Exception as e:
        handle_error(bot, update, MONEY_LIST_COMMAND, str(e))
        raise e

    date_str = operands[0]
    if date_str is None:
        date = update.message.date.date()
    else:
        try:
            date = parse(date_str).date()
        except Exception as e:
            handle_error(bot, update, MONEY_LIST_COMMAND, str(e))
            return

    try:
        values = goglemogle.money_list(user_group)
    except Exception as e:
        logging.error(e)
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
        raise e

    if not values:
        logging.error(msg="Empty response from google sheet")
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Oops. I cannot find anything.")
    else:
        try:
            print_money_list(bot, update, values, date)

        except Exception as e:
            logging.error(e)
            bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(e))
            raise e


def print_money_list(bot, update, values, date: datetime.date):
    money_str = ""
    expense_number = 0
    row_found_flag = False

    row_address = 1  # to start from 2
    for row in values:
        row_address += 1
        expense_date = parse(row[0]).date()
        if expense_date == date:
            row_found_flag = True
            expense_number += 1
            money_str += "[{row}] {date}; {cat}; {value}; {aim}\n" \
                         "".format(row=row_address, date=row[0], cat=row[1], value=row[2], aim=row[3])
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
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Nothing was found for date: {date}".format(date=date))
        logging.info(msg="no expenses for date {date}".format(date=date))


def money_edit_handler(bot, update):
    logging.info(msg="Editing a money record " + str(update.message))

    user_group = check_user_type(bot, update)
    if user_group != "d&j":
        return

    if update.message.text is None:
        handle_error(bot, update, MONEY_EDIT_COMMAND, 'No text provided')
        return

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)

    try:
        operands = get_operands(MONEY_EDIT_COMMAND, update.message.text)
    except Exception as e:
        handle_error(bot, update, MONEY_EDIT_COMMAND, str(e))
        raise e

    row_address = operands[0]
    if row_address is None:
        handle_error(bot, update, MONEY_EDIT_COMMAND, "No id provided")
        return

    expense_date = operands[1]
    category = operands[2]
    value = operands[3]
    aim = operands[4]

    if not (row_address and expense_date and category and value and aim):
        handle_error(bot, update, MONEY_EDIT_COMMAND, "All parameters have to be defined")
        return

    try:
        parse(expense_date).date()
        int(row_address)
        float(value)
        with lock:
            result = goglemogle.edit_expense(user_group, row_address, expense_date, category, value, aim)
    except Exception as e:
        handle_error(bot, update, MONEY_EDIT_COMMAND, "An error occurred: ", e)
        raise e

    logging.info(result)
    reply_msg = "{name}, я отредактировал расход {row}".format(name=update.message.from_user.first_name,
                                                               row=row_address)
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
