import re

from sirbot.slack.hookimpl import hookimpl
from sirbot.slack.message import Attachment


async def admin(message, slack, *_):
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


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': '^admin.*',
            'func': admin,
            'mention': True,
            'flags': re.IGNORECASE
        },
    ]

    return commands
