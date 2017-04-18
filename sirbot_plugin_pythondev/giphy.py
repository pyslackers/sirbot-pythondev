import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl

logger = logging.getLogger('sirbot.pythondev')


async def gif_search(message, slack, facades, *_):
    giphy = facades.get('giphy')
    search = message.incoming.text[10:].strip().split(' ')
    url = await giphy.search(search)
    message.text = url
    await slack.send(message)


async def gif_trending(message, slack, facades, *_):
    giphy = facades.get('giphy')
    url = await giphy.trending()
    message.text = url
    await slack.send(message)


async def gif_random(message, slack, facades, *_):
    giphy = facades.get('giphy')
    url = await giphy.random()
    message.text = url
    await slack.send(message)


async def gif_by_id(message, slack, facades, *_):
    giphy = facades.get('giphy')
    id_ = message.incoming.text[3:].strip()
    try:
        url = await giphy.by_id(id_)
        message.text = url
    except ConnectionError:
        message.text = '''I'm sorry I could not find this gif'''
    await slack.send(message)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': '^gif search ',
            'func': gif_search,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': '^gif$',
            'func': gif_random,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': '^gif trending$',
            'func': gif_trending,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': '^gif (?!search)(?!trending).*',
            'func': gif_by_id,
            'mention': True,
            'flags': re.IGNORECASE
        }
    ]

    return commands
