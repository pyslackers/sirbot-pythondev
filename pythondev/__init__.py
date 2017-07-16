from sirbot.core import hookimpl, Plugin, registry

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
        super().__init__(loop)
        self._loop = loop
        self._config = None
        self._session = None
        self._started = False

    async def configure(self, config, router, session):
        self._config = config
        self._session = session

    async def start(self):

        if 'scheduler' in registry:
            SchedulerJobs(self._config).add()

        if 'github' in registry:
            GitHubEndpoint(self._config).add()

        if 'slack' in registry:
            SlackEndpoint(self._config).add()

        self._started = True

    @property
    def started(self):
        return self._started
