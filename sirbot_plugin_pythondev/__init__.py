import re

from slack_sirbot.hookimpl import hookimpl
from slack_sirbot.message import Attachment


async def hello(message, slack, *_):
    message.text = 'Hello'
    await slack.send(message)


async def admin(message, slack, *_):
    incoming_text = message.incoming.text[5:].strip()
    title = 'New message from <@{frm}>'.format(frm=message.incoming.frm)
    att = Attachment(title=title, fallback=title, text=incoming_text)

    admin_message = message.clone()
    admin_message.attachments.append(att)
    admin_message.to = await slack.channels.get(name='admin')
    await slack.send(admin_message)

    message.text = 'Your message was successfully sent to the admin team'
    await slack.send(message)


async def intro_doc(message, slack, *_):
    message.text = 'https://pythondev.slack.com/files/mikefromit/F25EDF4KW/Intro_Doc'
    await slack.send(message)


async def what_to_do(message, slack, *_):
    message.text = 'https://pythondev.slack.com/files/ndevox/F4A137J0J/What_to_do_next_on_your_Python_journey'
    await slack.send(message)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': 'hello',
            'func': hello,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
        {
            'match': 'admin.*',
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
