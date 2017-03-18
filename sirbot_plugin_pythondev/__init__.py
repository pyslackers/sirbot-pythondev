import re
import asyncio
import logging

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment, SlackMessage, Field

logger = logging.getLogger('sirbot.pythondev')


async def hello(message, slack, *_):
    message.text = 'Hello'
    await slack.send(message)


async def admin(message, slack, _, facades):
    incoming_text = message.incoming.text[5:].strip()
    title = 'New message from <@{frm}>'.format(frm=message.incoming.frm.id)
    att = Attachment(title=title, fallback=title, text=incoming_text)

    admin_message = message.clone()
    admin_message.attachments.append(att)
    db = facades.get('database')
    admin_message.to = await slack.channels.get(name='admin', update=False, db=db)
    await slack.send(admin_message)

    message.text = 'Your message was successfully sent to the admin team'
    await slack.send(message)


async def intro_doc(message, slack, *_):
    message.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'
    await slack.send(message)


async def what_to_do(message, slack, *_):
    message.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'
    await slack.send(message)


async def team_join(event, slack, *_):
    message = SlackMessage()
    message.to = await slack.users.get(event['user']['id'], dm=True)
    message.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'
    await asyncio.sleep(60)
    await slack.send(message)


async def help_(message, slack, *_):
    message.text = 'Help of the good Sir-bot-a-lot'

    help_msg = Attachment(fallback='help', color='good', title='Common commands')
    hello_help = Field(title='Hello', value='Say hello to Sir-bot-a-lot.\n`@sir-bot-a-lot hello`', short=True)
    admin_help = Field(title='Admin', value='Send a message to the pythondev admin team.\n `@sir-bot-a-lot admin ...`', short=True)
    intro_doc_help = Field(title='Intro doc', value='Link the intro doc.\n `@sir-bot-a-lot intro doc`', short=True)
    what_to_do_help = Field(title='What to do', value='Link the what to do doc.\n `@sir-bot-a-lot what to do`', short=True)
    help_msg.fields.extend((hello_help, admin_help, intro_doc_help, what_to_do_help))

    gif_help = Attachment(fallback='gif help', color='good', title='Gif commands')
    gif_random_help = Field(title='Random', value='Get a random gif.\n`@sir-bot-a-lot gif`', short=True)
    gif_search_help = Field(title='Search', value='Search for a gif.\n`@sir-bot-a-lot gif search ...`', short=True)
    gif_trending_help = Field(title='Trending', value='Get a trending gif.\n`@sir-bot-a-lot gif trending`', short=True)
    gif_by_id_help = Field(title='By ID', value='''Get a gif by it's id.\n`@sir-bot-a-lot gif <gif_id>`''', short=True)
    gif_help.fields.extend((gif_random_help, gif_search_help, gif_trending_help, gif_by_id_help))

    message.attachments.extend((help_msg, gif_help))
    await slack.send(message)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': '^help',
            'func': help_,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'hello',
            'func': hello,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': '^admin.*',
            'func': admin,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'intro doc',
            'func': intro_doc,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'what to do',
            'func': what_to_do,
            'on_mention': True,
            'flags': re.IGNORECASE
        }
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
