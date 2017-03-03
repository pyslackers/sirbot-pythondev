import os
import aiohttp
import logging
import random
import pprint

logger = logging.getLogger('sirbot.pythondev')


class Giphy:

    ROOT_URL = 'http://api.giphy.com/v1/{}'
    SEARCH_TERM_URL = ROOT_URL.format('gifs/translate?s={terms}')
    TRENDING_URL = ROOT_URL.format('gifs/trending?')
    RANDOM_URL = ROOT_URL.format('gifs/random?')
    BY_ID_URL = ROOT_URL.format('gifs/{gif_id}?')

    def __init__(self):
        self._token = os.environ.get('SIRBOT_GIPHY_TOKEN') or "dc6zaTOxFJmzC"
        self._session = aiohttp.ClientSession()

    async def search(self, terms):
        data = await self._query(self.SEARCH_TERM_URL.format(terms='+'.join(terms)))
        return data['data']['images']['original']['url']

    async def trending(self):
        data = await self._query(self.TRENDING_URL)
        num = random.randint(0, len(data['data']) - 1)
        return data['data'][num]['images']['original']['url']

    async def random(self):
        data = await self._query(self.RANDOM_URL)
        num = random.randint(0, len(data['data']) - 1)
        return data['data']['image_url']

    async def by_id(self, id_):
        data = await self._query(self.BY_ID_URL.format(gif_id=id_))
        return data['data']['images']['original']['url']

    async def _query(self, url, method='GET'):
        if url.endswith('?'):
            url += 'api_key={}'.format(self._token)
        else:
            url += '&api_key={}'.format(self._token)

        logger.debug('Query giphy api with url: %s', url)
        rep = await self._session.request(method, url)
        data = await rep.json()

        if data['meta']['status'] != 200:
            raise ConnectionError
        return data

    def __del__(self):
        self._session.close()


async def gif_search(giphy, message, slack, *_):
    search = message.incoming.text[10:].strip().split(' ')
    url = await giphy.search(search)
    message.text = url
    await slack.send(message)

async def gif_trending(giphy, message, slack, *_):
    url = await giphy.trending()
    message.text = url
    await slack.send(message)

async def gif_random(giphy, message, slack, *_):
    url = await giphy.random()
    message.text = url
    await slack.send(message)

async def gif_by_id(giphy, message, slack, *_):
    id_ = message.incoming.text[3:].strip()
    try:
        url = await giphy.by_id(id_)
        message.text = url
    except ConnectionError:
        message.text = '''I'm sorry I could not find this gif'''
    await slack.send(message)
