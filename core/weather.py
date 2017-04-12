# coding=utf-8

import logging

import requests
import yaml
from telegram import ChatAction

from utils.commands import handle_error
from utils.user_check import get_user_group

log = logging.getLogger(__name__)

with open("config/config.yaml", 'r') as stream:
    config = yaml.load(stream)
LINK = config.get('weatherapi')
log.info("Weather api url: {}".format(LINK))

def current_weather(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    user = update.message.from_user.username
    user_group = get_user_group(user)
    if user_group is None:
        handle_error(bot, update, None, "Access denied")
        return

    log.info(msg="Finding out current weather... ")
    try:
        reply_msg = get_weather_msg(update.message.from_user.first_name)
    except EnvironmentError as e:
        handle_error(bot, update, None, "Unable to get weather data", e)
        return

    bot.sendMessage(chat_id=update.message.chat_id, text=reply_msg)


def get_weather_msg(name):
    resp = requests.get(LINK)
    if resp.status_code != 200:
        # This means something went wrong.
        # bot.sendMessage(chat_id=update.message.chat_id, text="Sorry,\n" + str(resp.status_code))
        raise EnvironmentError('GET /weather?lat=59.95&lon=30.21 {}'.format(resp.status_code))

    log.info(resp.json())
    temp_kelv = float(resp.json().get('main').get('temp'))
    temp_celcius = temp_kelv - 273.15
    humidity = resp.json().get('main').get('humidity')
    pressure_hpa = float(resp.json().get('main').get('pressure'))
    pressure_mmhg = pressure_hpa * 0.75006
    wind_speed = resp.json().get('wind').get('speed')
    descr = resp.json().get('weather')[0].get('description')

    reply_msg = name + ", погода в СПб:\n" \
                + descr + "\n" \
                + "Температура: " + str(round(temp_celcius, 1)) + " \u2103\n" \
                + "Давление: " + str(round(pressure_mmhg, 2)) + " мм рт.ст.\n" \
                + "Влажность: " + str(humidity) + " %\n" \
                + "Скорость ветра: " + str(wind_speed) + " м/c"
    log.info(reply_msg)
    return reply_msg
