import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl

logger = logging.getLogger('sirbot.pythondev')


async def gif_search(message, slack, facades, *_):
    response = message.response()
    giphy = facades.get('giphy')
    search = message.text[10:].strip().split(' ')
    url = await giphy.search(search)
    response.text = url
    await slack.send(response)


async def gif_trending(message, slack, facades, *_):
    response = message.response()
    giphy = facades.get('giphy')
    url = await giphy.trending()
    response.text = url
    await slack.send(response)


async def gif_random(message, slack, facades, *_):
    response = message.response()
    giphy = facades.get('giphy')
    url = await giphy.random()
    response.text = url
    await slack.send(response)


async def gif_by_id(message, slack, facades, *_):
    response = message.response()
    giphy = facades.get('giphy')
    id_ = message.text[3:].strip()
    try:
        url = await giphy.by_id(id_)
        response.text = url
    except ConnectionError:
        response.text = '''I'm sorry I could not find this gif'''
    await slack.send(response)


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
