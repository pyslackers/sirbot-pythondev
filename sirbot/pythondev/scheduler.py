import logging

from sirbot.slack.message import SlackMessage

logger = logging.getLogger(__name__)

LOOKING = '''*Weekly who's looking thread !*

If you are looking for a job please post your resume in this thread.'''

LOOKING_TIPS = '''We are an international community so please include your
location and if you are willing to relocate.'''

HIRING = '''*Weekly who's hiring thread !*

If you are looking for someone please post your job in this thread.'''

HIRING_TIPS = '''We are an international community so please include your \
company location and policy on remote employees. A good post should include \
the name of the company, the location, on-site/remote and a quick summary of \
the job offer'''


def add_to_scheduler(scheduler):
    scheduler.add_job('looking_for_job', looking_for_job,
                      trigger='cron', day_of_week=0, hour=8)
    scheduler.add_job('hiring', hiring,
                      trigger='cron', day_of_week=0, hour=8)


async def looking_for_job(facade):
    slack = facade.get('slack')

    channel = await slack.channels.get(name='python_jobs')
    message = SlackMessage(to=channel)
    message.text = LOOKING
    await slack.send(message)

    message_tips = SlackMessage(to=channel)
    message_tips.text = LOOKING_TIPS
    message_tips.thread = message.thread
    await slack.send(message_tips)


async def hiring(facade):
    slack = facade.get('slack')

    channel = await slack.channels.get(name='python_jobs')
    message = SlackMessage(to=channel)
    message.text = HIRING
    await slack.send(message)

    message_tips = SlackMessage(to=channel)
    message_tips.text = HIRING_TIPS
    message_tips.thread = message.thread
    await slack.send(message_tips)
