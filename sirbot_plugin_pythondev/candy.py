import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment, SlackMessage

logger = logging.getLogger('sirbot.pythondev')

TRIGGER = ':bdfl:'
USER_REGEX = re.compile('<@U.{8}>')
TRIGGER_REGEX = re.compile(TRIGGER)


async def add_candy_message(message, slack, facades, *_):
    users_raw = USER_REGEX.findall(message.text)
    users = [user[2:-1] for user in users_raw if
             user[2:-1] != message.frm.id]

    if not users:
        return

    candy = facades.get('candy')
    response = message.response()
    count = len(TRIGGER_REGEX.findall(message.text))

    receivers_messages = list()
    for user in users:
        slack_user = await slack.users.get(user, dm=True)
        user_count = await candy.add(user, count)
        msg = response.clone()
        msg.to = slack_user
        msg.text = '<@{sender}> gave you {count} {trigger}. You now have ' \
                   '{user_count} {trigger}'.format(sender=message.frm.id,
                                                   count=count,
                                                   trigger=TRIGGER,
                                                   user_count=user_count)
        receivers_messages.append(msg)

    response.to = message.frm
    response.text = 'You gave {count} {trigger} to <@{user}>'.format(
        count=count,
        trigger=TRIGGER,
        user=', '.join(users))

    await slack.send(response)
    for msg in receivers_messages:
        await slack.send(msg)


async def add_candy_reaction(event, slack, facades):
    if event['reaction'] == 'bdfl' and event['user'] != event['item_user']:
        candy = facades.get('candy')
        user_count = await candy.add(event['item_user'])

        message_from = SlackMessage(
            to=(await slack.users.get(event['user'], dm=True)))
        message_from.text = 'You gave 1 {trigger} to <@{user}>'.format(
            trigger=TRIGGER, user=event['item_user'])

        message_to = SlackMessage(
            to=(await slack.users.get(event['item_user'], dm=True)))
        message_to.text = '<@{sender}> gave you 1 {trigger}. ' \
                          'You now have {user_count} ' \
                          '{trigger}'.format(sender=event['user'],
                                             trigger=TRIGGER,
                                             user_count=user_count)
        await slack.send(message_from)
        await slack.send(message_to)

    else:
        return


async def leaderboard(command, slack, facades):
    response = command.response()

    candy = facades.get('candy')
    data = await candy.top(count=10)
    att = Attachment(
        title='{} Leaderboard'.format(TRIGGER),
        fallback='{} Leaderboard'.format(TRIGGER),
        color='good'
    )

    if not data:
        response.text = 'No data to display'
    else:
        response.response_type = 'in_channel'
        for user in data:
            slack_user = await slack.users.get(user['user'])
            att.text += '{} *{}*\n'.format(slack_user.name, user['candy'])

        response.attachments.append(att)

    await slack.send(response)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': TRIGGER,
            'func': add_candy_message,
        },
    ]

    return commands


@hookimpl
def register_slack_commands():
    commands = [
        {
            'command': '/leaderboard',
            'func': leaderboard,
            'public': False
        }
    ]

    return commands


@hookimpl
def register_slack_events():
    events = [
        {
            'event': 'reaction_added',
            'func': add_candy_reaction
        },
    ]

    return events
