from sirbot.core import hookimpl, Plugin

from .github import add_to_github
from .slack import add_to_slack


@hookimpl
def plugins(loop):
    return PythondevPlugin(loop)


class PythondevPlugin(Plugin):

    __version__ = '0.0.1'
    __name__ = 'pythondev'

    def __init__(self, loop):
        self._loop = loop
        self._config = None
        self._session = None
        self._facades = None
        self._started = False

    async def configure(self, config, router, session, facades):
        self._config = config
        self._session = session
        self._facades = facades

    async def start(self):

        if 'github' in self._facades:
            github_facade = self._facades.get('github')
            add_to_github(github_facade)

        if 'slack' in self._facades:
            slack_facade = self._facades.get('slack')
            add_to_slack(slack_facade)

        self._started = True

    @property
    def started(self):
        return self._started
