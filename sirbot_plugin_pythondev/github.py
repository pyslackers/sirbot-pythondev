import logging

from sirbot.plugins.github.hookimpl import hookimpl
from sirbot.slack.message import SlackMessage, Attachment

logger = logging.getLogger('sirbot.pythondev')


async def issues(event, facades):
    att = None

    if event['action'] == 'opened':
        att = issue_format(event, 'good')
    elif event['action'] == 'closed':
        att = issue_format(event, 'danger')

    if att:
        slack = facades.get('slack')
        channel = await slack.channels.get(name='community-projects')
        msg = SlackMessage(to=channel)
        msg.attachments.append(att)
        await slack.send(msg)


def issue_format(event, color):

    att = Attachment(
        fallback='issue {}'.format(event['action']),
        pretext='Issue {action} in <{url}|{name}>'.format(
            url=event['repository']['html_url'],
            name=event['repository']['name'],
            action=event['action']
        ),
        color=color,
        text=event['issue']['body'],
        title=event['issue']['title'],
        title_link=event['issue']['html_url'],
        author_icon=event['sender']['avatar_url'],
        author_name=event['sender']['login'],
        author_link=event['sender']['html_url'],
        footer=', '.join(label['name'] for label in event['issue']['labels'])
    )

    return att


async def pull_request(event, facades):
    att = None

    if event['action'] == 'opened':
        data = {'color': 'good', 'action': 'opened'}
        att = pull_request_format(event, data)
    elif event['action'] == 'closed':
        if event['merged']:
            data = {'color': '#6f42c1', 'action': 'merged'}
        else:
            data = {'color': 'danger', 'action': 'closed'}

        att = pull_request_format(event, data)

    if att:
        slack = facades.get('slack')
        channel = await slack.channels.get(name='community-projects')
        msg = SlackMessage(to=channel)
        msg.attachments.append(att)
        await slack.send(msg)


def pull_request_format(event, data):

    footer = '+ {add} / - {del_}'.format(
        add=event['pull_request']['additions'],
        del_=event['pull_request']['deletions']
    )

    att = Attachment(
        fallback='pull request {}'.format(data['action']),
        pretext='Pull request {action} in <{url}|{name}>'.format(
            url=event['repository']['html_url'],
            name=event['repository']['name'],
            action=data['action']
        ),
        color=data['color'],
        text=event['pull_request']['body'],
        title=event['pull_request']['title'],
        title_link=event['pull_request']['html_url'],
        author_icon=event['sender']['avatar_url'],
        author_name=event['sender']['login'],
        author_link=event['sender']['html_url'],
        footer=footer
    )

    return att


@hookimpl
def register_github_events():

    events = [
        {
            'event': 'issues',
            'func': issues
        },
        {
            'event': 'pull_request',
            'func': pull_request
        }

    ]

    return events
