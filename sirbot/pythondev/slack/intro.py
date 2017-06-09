import asyncio

from sirbot.slack.message import SlackMessage

INTRO_URL = 'https://github.com/pyslackers/community/blob/master/' \
            'introduction.md'

INTRO_TEXT = '''Welcome to the community :tada:


We are glad that you have decided to join us. We have documented a few things
in the <{}|intro doc> to help you along from the beginning because
we are grand believers in the Don't Repeat Yourself principle, and it just
seems so professional!

May your :taco:s be plentiful!'''.format(INTRO_URL)


def add_to_slack(slack):
    slack.add_event('team_join', team_join)


async def team_join(event, slack, _):
    await asyncio.sleep(60)
    to = await slack.users.get(event['user']['id'], dm=True)
    message = SlackMessage(to=to)
    message.text = INTRO_TEXT
    await slack.send(message)
