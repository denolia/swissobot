from collections import namedtuple

BOT_NAME = '@DnJTodoBot'
SEPARATOR = ';'

Command = namedtuple('Command', 'name, max_operands, format, example')

MONEY_COMMAND = Command(name='money', max_operands=3, format='/money сумма [; цель; дата]',
                        example='/money 100; котята; 05.03')


# moneylist = Command(name='moneylist', max_operands=1, format='/moneylist [дата]', example='/money 100; котята; 05.03')


def get_operands(command: Command, message: str) -> list:
    operands = message.replace('/{}'.format(command.name), '').replace(BOT_NAME, '').strip().split(SEPARATOR)
    result = []

    if len(operands) > command.max_operands:
        raise ValueError("Too many arguments")

    for i, _ in enumerate(operands):
        result.append(operands[i].strip())
        if result[i] is "":
            result[i] = None

    while len(result) < command.max_operands:
        result.append(None)

    return result
