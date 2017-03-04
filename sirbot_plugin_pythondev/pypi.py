import os
import aiohttp
import logging
import random
import re
import asyncio
import functools
import json


from aiohttp_xmlrpc.client import ServerProxy
from distance import levenshtein
from operator import itemgetter

from sirbot_plugin_slack.hookimpl import hookimpl
from sirbot_plugin_slack.message import Attachment, SlackMessage
logger = logging.getLogger('sirbot.pythondev')


class PyPi:
    ROOT_URL = 'https://pypi.python.org/pypi'
    SEARCH_PATH = '?%3Aaction=search&term={0}&submit=search'

    def __init__(self):
        self._session = aiohttp.ClientSession()
        self.client = ServerProxy(self.ROOT_URL)

    def _result_to_attachment(self, item):
        return Attachment(
            title=item['name'],
            fallback=item['name'],
            text=item['summary'],
            title_link='{}/{}'.format(self.ROOT_URL, item['name'])
        )

    async def pypi_search(self, term):
        results = await self.client.search({'name': term})
        for item in results:
            item['distance'] = levenshtein(str(term), item["name"])
        results.sort(key=itemgetter('distance'))

        results = [self._result_to_attachment(item) for item in results]
        if len(results) > 3:
            path = self.SEARCH_PATH.format(term)
            more_info = Attachment(
                title='{0} more result(s)..'.format(len(results)-3),
                fallback='{0} more result(s)..'.format(len(results)-3),
                title_link='{}/{}'.format(self.ROOT_URL, path)
            )
            results = results[:3]
            results.append(more_info)
        return results

    def __del__(self):
        self._session.close()
        self.client.close()

async def pypi_search(pypi, message, slack, *_):
    search = message.incoming.text[11:].strip()
    result = await pypi.pypi_search(search)
    message.content.attachments = result
    message.text = "Searched PyPi for '{0}'".format(search)
    await slack.send(message)


@hookimpl
def register_slack_messages():
    pypi = PyPi()
    pypy_search_name = asyncio.coroutine(functools.partial(pypi_search, pypi))
    commands = [
        {
            'match': '^pypi search ',
            'func': pypy_search_name,
            'on_mention': True,
            'flags': re.IGNORECASE
        },
    ]

    return commands
