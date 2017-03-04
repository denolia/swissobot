# coding=utf-8

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
    temp_kelv = float(resp.json().get('main').get('temp'))
    temp_celcius = temp_kelv - 273.15
    humidity = resp.json().get('main').get('humidity')
    pressure_hpa = float(resp.json().get('main').get('pressure'))
    pressure_mmhg = pressure_hpa * 0.75006
    wind_speed = resp.json().get('wind').get('speed')
    descr = resp.json().get('weather')[0].get('description')

    reply_msg = update.message.from_user.first_name + ", погода в СПб:\n" \
                + descr + "\n" \
                + "Температура: " + str(round(temp_celcius, 1)) + " \u2103\n" \
                + "Давление: " + str(round(pressure_mmhg, 2)) + " мм рт.ст.\n" \
                + "Влажность: " + str(humidity) + " %\n" \
                + "Скорость ветра: " + str(wind_speed) + " м/c"
    logging.info(reply_msg)

    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)
