from sirbot.core import hookimpl, Plugin

from .github import GitHubEndpoint
from .scheduler import SchedulerJobs
from .slack import SlackEndpoint


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

        if 'scheduler' in self._facades:
            scheduler_facade = self._facades.get('scheduler')
            SchedulerJobs(self._config).add(scheduler_facade)

        if 'github' in self._facades:
            github_facade = self._facades.get('github')
            GitHubEndpoint(self._config).add(github_facade)

        if 'slack' in self._facades:
            slack_facade = self._facades.get('slack')
            SlackEndpoint(self._config).add(slack_facade)

        self._started = True

    @property
    def started(self):
        return self._started
