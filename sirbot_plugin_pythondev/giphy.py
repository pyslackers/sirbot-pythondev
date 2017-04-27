import logging
import re
import json

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment, Button

logger = logging.getLogger('sirbot.pythondev')


async def gif_search(command, slack, facades):
    response = command.response()
    giphy = facades.get('giphy')
    urls = await giphy.search(command.text)

    att = Attachment(
        title='Giphy search: `{}`'.format(command.text),
        fallback='Giphy search: `{}`'.format(command.text),
        image_url=urls[0],
        callback_id='gif_search'
    )

    data = json.dumps({'urls': urls, 'search': command.text, 'index': 0})
    ok = Button(name='ok', text='Send', style='primary', value=data)
    again = Button(name='again', text='Search again', value=data)

    att.actions = [ok, again]
    response.attachments.append(att)
    await slack.send(response)


async def gif_search_action(action, slack, facades):
    response = action.response()
    data = json.loads(action.action['value'])

    if action.action['name'] == 'ok':
        title = '<@{}> Searched giphy for: `{}`'.format(action.user.id,
                                                        data['search'])

        att = Attachment(
            title=title,
            fallback=title,
            image_url=data['urls'][data['index']],
        )

        response.attachments.append(att)
        response.replace_original = False
        await slack.send(response)

        confirm = action.response()
        confirm.text = 'Gif successfully sent'
        await slack.send(confirm)

    elif action.action['name'] == 'again':

        index = data['index'] + 1
        urls = data['urls']

        try:
            url = urls[index]
        except IndexError:
            response.text = 'No more result to display'
            await slack.send(response)
            return

        att = Attachment(
            title='Giphy search: `{}`'.format(data['search']),
            fallback='Giphy search: `{}`'.format(data['search']),
            image_url=url,
            callback_id='gif_search'
        )

        data = json.dumps({'urls': urls,
                           'search': data['search'],
                           'index': index})
        ok = Button(name='ok', text='Send', style='primary', value=data)
        again = Button(name='again', text='Search again', value=data)

        att.actions = [ok, again]
        response.attachments.append(att)
        await slack.send(response)
    else:
        return

# async def gif_trending(message, slack, facades, *_):
#     response = message.response()
#     giphy = facades.get('giphy')
#     url = await giphy.trending()
#     response.text = url
#     await slack.send(response)
#
#
# async def gif_random(message, slack, facades, *_):
#     response = message.response()
#     giphy = facades.get('giphy')
#     url = await giphy.random()
#     response.text = url
#     await slack.send(response)
#
#
# async def gif_by_id(message, slack, facades, *_):
#     response = message.response()
#     giphy = facades.get('giphy')
#     id_ = message.text[3:].strip()
#     try:
#         url = await giphy.by_id(id_)
#         response.text = url
#     except ConnectionError:
#         response.text = '''I'm sorry I could not find this gif'''
#     await slack.send(response)


# @hookimpl
# def register_slack_messages():
#     commands = [
#         {
#             'match': '^gif search ',
#             'func': gif_search,
#             'mention': True,
#             'flags': re.IGNORECASE
#         },
#         {
#             'match': '^gif$',
#             'func': gif_random,
#             'mention': True,
#             'flags': re.IGNORECASE
#         },
#         {
#             'match': '^gif trending$',
#             'func': gif_trending,
#             'mention': True,
#             'flags': re.IGNORECASE
#         },
#         {
#             'match': '^gif (?!search)(?!trending).*',
#             'func': gif_by_id,
#             'mention': True,
#             'flags': re.IGNORECASE
#         }
#     ]
#
#     return commands


@hookimpl
def register_slack_commands():
    commands = [
        {
            'command': '/gif',
            'func': gif_search,
            'public': False
        }
    ]

    return commands


@hookimpl
def register_slack_actions():
    commands = [
        {
            'callback_id': 'gif_search',
            'func': gif_search_action,
            'public': False
        }
    ]

    return commands
