import asyncio
import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment, SlackMessage, Field

logger = logging.getLogger('sirbot.pythondev')

PUBLISH_SHORTCUT = {
    '$feedback': 'https://docs.google.com/forms/d/e/1FAIpQLSfuM15Y5ObMDgFKOpeOEjYhUm9h4QW4VQ7mBXWcs9oOrjt0EQ/viewform?usp=sf_link'  # noqa
}


async def hello(message, slack, *_):
    response = message.response()
    response.text = 'Hello'
    await slack.send(response)


async def admin(message, slack, facades, _):
    response = message.response()
    title = 'New message from <@{frm}>'.format(frm=message.frm.id)
    att = Attachment(
        title=title,
        fallback=title,
        text=message.text[5:].strip()
    )

    admin_message = response.clone()
    admin_message.attachments.append(att)
    admin_message.to = await slack.channels.get(name='admin', update=False)
    await slack.send(admin_message)

    message.text = 'Your message was successfully sent to the admin team'
    await slack.send(response)


async def intro_doc(message, slack, *_):
    response = message.response()
    response.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'  # noqa
    await slack.send(response)


async def what_to_do(message, slack, *_):
    response = message.response()
    response.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'  # noqa
    await slack.send(response)


async def publish(message, slack, _, match):
    response = message.response()

    to_id = match.group('to_id')
    item = match.group('item')

    if to_id.startswith('C'):
        to = await slack.channels.get(to_id)
        if to.is_member:
            response.text = PUBLISH_SHORTCUT.get(item, item)
            response.to = to
        else:
            response.text = 'Sorry I can not publish is this channel.' \
                            ' I am not a member.'
            response.to = response.frm

    elif to_id.startswith('U'):
        to = await slack.users.get(to_id, dm=True)
        response.text = PUBLISH_SHORTCUT.get(item, item)
        response.to = to
    else:
        response.text = 'Sorry I can not understand the destination.'
        response.to = response.frm

    await slack.send(response)


async def team_join(event, slack, _):
    await asyncio.sleep(60)
    to = await slack.users.get(event['user']['id'], dm=True)
    message = SlackMessage(to=to)
    message.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'  # noqa
    await slack.send(message)


async def help_(message, slack, *_):
    response = message.response()
    response.text = 'Help of the good Sir-bot-a-lot'

    help_msg = Attachment(fallback='help', color='good',
                          title='Common commands')
    hello_help = Field(title='Hello',
                       value='Say hello to Sir-bot-a-lot.'
                             '\n`@sir-bot-a-lot hello`',
                       short=True)
    admin_help = Field(title='Admin',
                       value='Send a message to the pythondev admin team.'
                             '\n `@sir-bot-a-lot admin ...`',
                       short=True)
    intro_doc_help = Field(title='Intro doc',
                           value='Link the intro doc.'
                                 '\n `@sir-bot-a-lot intro doc`',
                           short=True)
    what_to_do_help = Field(title='What to do',
                            value='Link the what to do doc.'
                                  '\n `@sir-bot-a-lot what to do`',
                            short=True)
    help_msg.fields.extend(
        (hello_help, admin_help, intro_doc_help, what_to_do_help))

    gif_help = Attachment(fallback='gif help', color='good',
                          title='Gif commands')
    gif_random_help = Field(title='Random',
                            value='Get a random gif.\n`@sir-bot-a-lot gif`',
                            short=True)
    gif_search_help = Field(title='Search',
                            value='Search for a gif.'
                                  '\n`@sir-bot-a-lot gif search ...`',
                            short=True)
    gif_trending_help = Field(title='Trending',
                              value='Get a trending gif.'
                                    '\n`@sir-bot-a-lot gif trending`',
                              short=True)
    gif_by_id_help = Field(title='By ID',
                           value='''Get a gif by it's id.
                           \n`@sir-bot-a-lot gif <gif_id>`''',
                           short=True)
    gif_help.fields.extend(
        (gif_random_help, gif_search_help, gif_trending_help, gif_by_id_help))

    response.attachments.extend((help_msg, gif_help))
    await slack.send(response)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': '^help',
            'func': help_,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'hello',
            'func': hello,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': '^admin.*',
            'func': admin,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'intro doc',
            'func': intro_doc,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'what to do',
            'func': what_to_do,
            'mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'tell (<(#|@)(?P<to_id>[A-Z0-9]*)(|.*)?>) (?P<item>.*)',
            'func': publish,
            'mention': True,
            'flags': re.IGNORECASE,
            'admin': True

        },
    ]

    return commands


@hookimpl
def register_slack_events():
    commands = [
        {
            'name': 'team_join',
            'func': team_join
        }
    ]

    return commands
