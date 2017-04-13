import logging
import re

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment

logger = logging.getLogger('sirbot.pythondev')


async def pypi_search(message, slack, facades, *_):
    search = message.incoming.text[11:].strip()
    pypi = facades.get('pypi')
    results = await pypi.pypi_search(search)

    if results:
        for result in results[:3]:
            att = Attachment(
                title=result['name'],
                fallback=result['name'],
                text=result['summary'],
                title_link='{}/{}'.format(pypi.ROOT_URL, result['name'])
            )
            message.content.attachments.append(att)

        if len(results) > 3:
            path = pypi.SEARCH_PATH.format(search)
            more_info = Attachment(
                title='{0} more result(s)..'.format(len(results) - 3),
                fallback='{0} more result(s)..'.format(len(results) - 3),
                title_link='{}/{}'.format(pypi.ROOT_URL, path)
            )
            message.content.attachments.append(more_info)

        message.text = "Searched PyPi for '{0}'".format(search)
    else:
        message.text = "Could not find anything on PyPi matching '{0}'".format(search)

    await slack.send(message)


@hookimpl
def register_slack_messages():
    commands = [
        {
            'match': '^pypi search ',
            'func': pypi_search,
            'mention': True,
            'flags': re.IGNORECASE
        },
    ]

    return commands
