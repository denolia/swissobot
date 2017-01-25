import logging

from telegram import ChatAction

from user_check import allowed_user


def current_weather(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    if not allowed_user(bot, update):
        return

    logging.info(msg="Finding out current weather... ")
    link = "http://api.openweathermap.org/data/2.5/weather?lat=59.95&lon=30.21&appid=d9022c300d4c076fd764ce33996e75ac"
    import requests

    resp = requests.get(link)
    if resp.status_code != 200:
        # This means something went wrong.
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(resp.status_code))
        raise EnvironmentError('GET /weather?lat=59.95&lon=30.21 {}'.format(resp.status_code))

    logging.info(resp.json())
    reply_msg = update.message.from_user.first_name + ", погода в СПб " + str(resp.json())
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def current_weather(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    if not allowed_user(bot, update):
        return

    logging.info(msg="Finding out current weather... ")
    link = "http://api.openweathermap.org/data/2.5/weather?lat=59.95&lon=30.21&appid=d9022c300d4c076fd764ce33996e75ac"
    import requests

    resp = requests.get(link)
    if resp.status_code != 200:
        # This means something went wrong.
        bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(resp.status_code))
        raise EnvironmentError('GET /weather?lat=59.95&lon=30.21 {}'.format(resp.status_code))

    logging.info(resp.json())
    reply_msg = update.message.from_user.first_name + ", погода в СПб " + str(resp.json())
    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
