# coding=utf-8

import logging
from typing import Optional

allowed_users = ('daniilbubnov', 'julia_vikulina')
user_group = {'d&j': ['daniilbubnov', 'julia_vikulina'],
              'dad': ['Vikulinonline']}
log = logging.getLogger(__name__)


def allowed_user(bot, update) -> bool:
    if update.message.from_user.username not in allowed_users:
        bot.sendMessage(chat_id=update.message.chat_id, text="Access denied")
        return False
    return True

# TODO clarify that
def check_user_type(bot, update) -> str:
    for group in user_group:
        if update.message.from_user.username in user_group.get(group):
            return group

    bot.sendMessage(chat_id=update.message.chat_id, text="Access denied")
    log.info("Access denied for " + update.message.from_user.username)
    return ""


def get_user_group(user) -> Optional[str]:
    for group in user_group:
        if user in user_group.get(group):
            return group


if __name__ == "__main__":
    import doctest

    doctest.testmod()
