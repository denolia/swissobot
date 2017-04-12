# coding=utf-8

import logging
from typing import Optional

allowed_users = ('daniilbubnov', 'julia_vikulina')
user_group = {'d&j': ['daniilbubnov', 'julia_vikulina'],
              'dad': ['Vikulinonline']}
log = logging.getLogger(__name__)


def get_user_group(user) -> Optional[str]:
    for group in user_group:
        if user in user_group.get(group):
            return group
