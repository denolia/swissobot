import logging

allowed_users = ('daniilbubnov', 'julia_vikulina')
user_group = {'d&j': ['daniilbubnov', 'julia_vikulina'],
              'dad': []}


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="Access denied")
        return False
    return True


def check_user_type(bot, update) -> str:
    for group in user_group:
        if update.message.from_user.username not in user_group.get(group):
            bot.sendMessage(chat_id=update.message.chat_id, text="Access denied")
            return group
    logging.info("Access denied for " + update.message.from_user.username)
    return ""
