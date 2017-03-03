from aiohttp.web import Response

from sirbot_plugin_web.hookimpl import hookimpl
from sirbot_plugin_slack.message import SlackMessage

async def test(request, facades):
    slack = facades.get('sirbot_plugin_slack')
    msg = SlackMessage()
    msg.to = await slack.channels.get(name='bots')
    msg.text = 'Test web url'
    await slack.send(msg)
    return Response(text='ok')


@hookimpl
def register_web_endpoints():
    endpoints = [
        {
            'method': 'GET',
            'url': '/',
            'func': test
        }
    ]

    return endpoints
