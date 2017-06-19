import logging

from sirbot.slack.message import SlackMessage

logger = logging.getLogger(__name__)


class SchedulerJobs:

    def __init__(self, config):
        self.config = config

    def add(self, scheduler):
        scheduler.add_job('looking_for_job', self.looking_for_job,
                          trigger='cron', day_of_week=0, hour=8)
        scheduler.add_job('hiring', self.hiring,
                          trigger='cron', day_of_week=0, hour=8)

    async def looking_for_job(self, facade):
        slack = facade.get('slack')

        channel = await slack.channels.get(name='python_jobs')
        message = SlackMessage(to=channel)
        message.text = self.config['python_jobs']['looking']
        await slack.send(message)

        message_tips = SlackMessage(to=channel)
        message_tips.text = self.config['python_jobs']['looking_tips']
        message_tips.thread = message.thread
        await slack.send(message_tips)

    async def hiring(self, facade):
        slack = facade.get('slack')

        channel = await slack.channels.get(name='python_jobs')
        message = SlackMessage(to=channel)
        message.text = self.config['python_jobs']['hiring']
        await slack.send(message)

        message_tips = SlackMessage(to=channel)
        message_tips.text = self.config['python_jobs']['hiring_tips']
        message_tips.thread = message.thread
        await slack.send(message_tips)
