import logging

from sirbot.slack.message import SlackMessage, Attachment

logger = logging.getLogger(__name__)


class GitHubEndpoint:

    def __init__(self, config):
        self.config = config

    def add(self, github):
        github.add_event('issues', self.issues)
        github.add_event('pull_request', self.pull_request)

    async def issues(self, event, facades):
        att = None

        if event['action'] == 'opened':
            att = self._issue_format(event, 'good')
        elif event['action'] == 'closed':
            att = self._issue_format(event, 'danger')

        if att:
            slack = facades.get('slack')
            channel = await slack.channels.get(
                name=self.config['github']['channel']
            )
            msg = SlackMessage(to=channel)
            msg.attachments.append(att)
            await slack.send(msg)

    def _issue_format(self, event, color):
        att = Attachment(
            fallback='issue {}'.format(event['action']),
            color=color,
            text=event['issue']['body'],
            title='Issue {action} in <{repo_url}|{name}>:'
                  ' <{url}|{title}>'.format(
                repo_url=event['repository']['html_url'],
                url=event['issue']['html_url'],
                name=event['repository']['name'],
                action=event['action'],
                title=event['issue']['title']
            ),
            author_icon=event['sender']['avatar_url'],
            author_name=event['sender']['login'],
            author_link=event['sender']['html_url'],
            footer=', '.join(
                label['name'] for label in event['issue']['labels']
            )
        )

        return att

    async def pull_request(self, event, facades):
        att = None

        if event['action'] == 'opened':
            data = {'color': 'good', 'action': 'opened'}
            att = self._pull_request_format(event, data)
        elif event['action'] == 'closed':
            if event['pull_request']['merged']:
                data = {'color': '#6f42c1', 'action': 'merged'}
            else:
                data = {'color': 'danger', 'action': 'closed'}

            att = self._pull_request_format(event, data)

        if att:
            slack = facades.get('slack')
            channel = await slack.channels.get(
                name=self.config['github']['channel']
            )
            msg = SlackMessage(to=channel)
            msg.attachments.append(att)
            await slack.send(msg)

    def _pull_request_format(self, event, data):
        footer = '+ {add} / - {del_}'.format(
            add=event['pull_request']['additions'],
            del_=event['pull_request']['deletions']
        )

        att = Attachment(
            fallback='pull request {}'.format(data['action']),
            title='Pull request {action} in <{repo_url}|{name}>:'
                  ' <{url}|{title}>'.format(
                repo_url=event['repository']['html_url'],
                url=event['pull_request']['html_url'],
                name=event['repository']['name'],
                action=data['action'],
                title=event['pull_request']['title'],
            ),
            color=data['color'],
            text=event['pull_request']['body'],
            author_icon=event['sender']['avatar_url'],
            author_name=event['sender']['login'],
            author_link=event['sender']['html_url'],
            footer=footer
        )

        return att
