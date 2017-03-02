import os
import aiohttp
import pprint
import logging

logger = logging.getLogger('sirbot.pythondev')


class Giphy:

    ROOT_URL = 'http://api.giphy.com/v1/{}'
    SEARCH_TERM_URL = ROOT_URL.format('gifs/search?q={terms}&limit=1')

    def __init__(self):
        self._token = os.environ.get('SIRBOT_GIPHY_TOKEN') or "dc6zaTOxFJmzC"
        self._session = aiohttp.ClientSession()

    async def search(self, terms):
        url = self.SEARCH_TERM_URL.format(terms='+'.join(terms))
        return await self._query(url)

    async def _query(self, url, method='GET'):
        if url.endswith('?'):
            url += 'api_key={}'.format(self._token)
        else:
            url += '&api_key={}'.format(self._token)

        logger.debug('Query giphy api with url: %s', url)
        rep = await self._session.request(method, url)
        data = await rep.json()
        return data['data'][0]['images']['original']['url']
