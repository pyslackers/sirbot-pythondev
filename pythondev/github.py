import logging

from sirbot.core import registry
from sirbot.slack.message import SlackMessage, Attachment

logger = logging.getLogger(__name__)


class GitHubEndpoint:

    def __init__(self, config):
        self.config = config

    def add(self):
        github = registry.get('github')

        github.register(self.issues_opened, 'issues', action='opened')
        github.register(self.issues_closed, 'issues', action='closed')
        github.register(self.issues_reopened, 'issues', action='reopened')

        github.register(self.pr_opened, 'pull_request', action='opened')
        github.register(self.pr_closed, 'pull_request', action='closed')
        github.register(self.pr_reopened, 'pull_request', action='reopened')

        github.register(self.release_created, 'release', action='published')
        github.register(self.repo_created, 'repository', action='created')
        github.register(self.repo_deleted, 'repository', action='deleted')

    async def issues_opened(self, event):
        await self.send_issue_msg(event, 'good')

    async def issues_closed(self, event):
        await self.send_issue_msg(event, 'danger')

    async def issues_reopened(self, event):
        await self.send_issue_msg(event, 'good')

    async def send_issue_msg(self, issue, color):
        att = Attachment(
            fallback='issue {}'.format(issue.data['action']),
            color=color,
            text='*<{url}|{title}>*\n{body}'.format(
                url=issue.data['issue']['html_url'],
                title=issue.data['issue']['title'],
                body=issue.data['issue']['body']
            ),
            title='Issue {action} in <{repo_url}|{name}>'.format(
                repo_url=issue.data['repository']['html_url'],
                name=issue.data['repository']['name'],
                action=issue.data['action'],
            ),
            author_icon=issue.data['sender']['avatar_url'],
            author_name=issue.data['sender']['login'],
            author_link=issue.data['sender']['html_url'],
            footer=', '.join(
                label['name'] for label in issue.data['issue']['labels']
            )
        )

        slack = registry.get('slack')
        channel = await slack.channels.get(
            name=self.config['github']['channel']
        )
        msg = SlackMessage(to=channel)
        msg.attachments.append(att)
        await slack.send(msg)

    async def pr_opened(self, event):
        await self.send_pr_msg(event, 'opened', 'good')

    async def pr_closed(self, event):
        if event.data['pull_request']['merged']:
            await self.send_pr_msg(event, 'merged', '#6f42c1')
        else:
            await self.send_pr_msg(event, 'closed', 'danger')

    async def pr_reopened(self, event):
        await self.send_pr_msg(event, 'reopened', 'good')

    async def send_pr_msg(self, pr, action, color):
        footer = '+ {add} / - {del_}'.format(
            add=pr.data['pull_request']['additions'],
            del_=pr.data['pull_request']['deletions']
        )

        att = Attachment(
            fallback='pull request {}'.format(action),
            title='Pull request {action} in <{repo_url}|{name}>:'
                  ' <{url}|{title}>'.format(
                repo_url=pr.data['repository']['html_url'],
                url=pr.data['pull_request']['html_url'],
                name=pr.data['repository']['name'],
                action=pr.data['action'],
                title=pr.data['pull_request']['title'],
            ),
            color=color,
            text='*<{url}|{title}>*\n{body}'.format(
                url=pr.data['pull_request']['html_url'],
                title=pr.data['pull_request']['title'],
                body=pr.data['pull_request']['body']
            ),
            author_icon=pr.data['sender']['avatar_url'],
            author_name=pr.data['sender']['login'],
            author_link=pr.data['sender']['html_url'],
            footer=footer
        )

        slack = registry.get('slack')
        channel = await slack.channels.get(
            name=self.config['github']['channel']
        )
        msg = SlackMessage(to=channel)
        msg.attachments.append(att)
        await slack.send(msg)

    async def release_created(self, event):

        slack = registry.get('slack')
        channel = await slack.channels.get(
            name=self.config['github']['channel']
        )
        msg = SlackMessage(to=channel)
        msg.text = 'Release {release} created in {repo} by {user}'.format(
            release=event.data['release']['tag_name'],
            repo=event.data['repository']['name'],
            user=event.data['sender']['login']
        )
        await slack.send(msg)

    async def repo_created(self, event):

        slack = registry.get('slack')
        channel = await slack.channels.get(
            name=self.config['github']['channel']
        )
        msg = SlackMessage(to=channel)
        msg.text = 'Repository {repo} created by {user} :tada:'.format(
            repo=event.data['repository']['name'],
            user=event.data['sender']['login']
        )
        await slack.send(msg)

    async def repo_deleted(self, event):

        slack = registry.get('slack')
        channel = await slack.channels.get(
            name=self.config['github']['channel']
        )
        msg = SlackMessage(to=channel)
        msg.text = 'Repository {repo} deleted by {user} :cold_sweat:'.format(
            repo=event.data['repository']['name'],
            user=event.data['sender']['login']
        )
        await slack.send(msg)
