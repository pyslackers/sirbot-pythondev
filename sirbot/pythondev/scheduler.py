import logging

from sirbot.slack.message import SlackMessage

logger = logging.getLogger(__name__)


class SchedulerJobs:

    def __init__(self, config, registry):
        self.config = config
        self.registry = registry

    def add(self, scheduler):
        scheduler.add_job(self.looking_for_job, name='looking_for_job',
                          trigger='cron', day_of_week=0, hour=8)
        scheduler.add_job(self.hiring, name='hiring',
                          trigger='cron', day_of_week=0, hour=8)

    async def looking_for_job(self):
        slack = self.registry.get('slack')

        channel = await slack.channels.get(name='job_board')
        message = SlackMessage(to=channel)
        message.text = self.config['python_jobs']['looking']
        await slack.send(message)

        message_tips = SlackMessage(to=channel)
        message_tips.text = self.config['python_jobs']['looking_tips']
        message_tips.thread = message.thread
        await slack.send(message_tips)

    async def hiring(self):
        slack = self.registry.get('slack')

        channel = await slack.channels.get(name='job_board')
        message = SlackMessage(to=channel)
        message.text = self.config['python_jobs']['hiring']
        await slack.send(message)

        message_tips = SlackMessage(to=channel)
        message_tips.text = self.config['python_jobs']['hiring_tips']
        message_tips.thread = message.thread
        await slack.send(message_tips)
