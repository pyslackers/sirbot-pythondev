import re

from sirbot.slack.hookimpl import hookimpl


async def hello(message, slack, *_):
    response = message.response()
    response.text = 'Hello'
    await slack.send(response)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': 'hello',
            'func': hello,
            'mention': True,
            'flags': re.IGNORECASE
        },

    ]

    return commands
