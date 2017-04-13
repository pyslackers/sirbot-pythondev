import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment

logger = logging.getLogger('sirbot.candy')

TRIGGER = ':bdfl:'
USER_REGEX = re.compile('<@U.{8}>')
TRIGGER_REGEX = re.compile(TRIGGER)

async def add_candy(message, slack, facades, *_):
    candy = facades.get('candy')
    db = facades.get('database')
    users = USER_REGEX.findall(message.incoming.text)
    if not users:
        return

    count = len(TRIGGER_REGEX.findall(message.incoming.text))

    receivers_messages = list()
    for user in users:
        user = user[2:-1]
        slack_user = await slack.users.get(user, db=db, update=True, dm=True)
        user_count = await candy.add(user, count, db=db)
        msg = message.clone()
        msg.to = slack_user
        msg.text = '<@{sender}> gave you {count} {trigger}. You now have {user_count} {trigger}'.format(
            sender=message.incoming.frm.id,
            count=count,
            trigger=TRIGGER,
            user_count=user_count
        )
        receivers_messages.append(msg)

    message.to = message.incoming.frm
    message.text = 'You gave {count} {trigger} to {user}'.format(count=count,
                                                                 trigger=TRIGGER,
                                                                 user=', '.join(users))
    await slack.send(message)
    for msg in receivers_messages:
        await slack.send(msg)
    await db.commit()


async def leaderboard(message, slack, facades, *_):
    candy = facades.get('candy')
    db = facades.get('database')
    data = await candy.top(count=10, db=db)
    att = Attachment(title='{} Leaderboard'.format(TRIGGER),
                     fallback='{} Leaderboard'.format(TRIGGER),
                     color='good')
    att.data['text'] = ''

    for user in data:
        slack_user = await slack.users.get(user['user'], db=db, update=True)
        att.data['text'] += '{} *{}*\n'.format(slack_user.slack_data['name'], user['candy'])

    message.attachments.append(att)
    await slack.send(message)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': TRIGGER,
            'func': add_candy,
        },
        {
            'match': 'leaderboard',
            'func': leaderboard,
            'mention': True,
            'flags': re.IGNORECASE
        }
    ]

    return commands
