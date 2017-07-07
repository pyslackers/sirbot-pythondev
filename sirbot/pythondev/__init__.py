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
        super().__init__(loop)
        self._loop = loop
        self._config = None
        self._session = None
        self._registry = None
        self._started = False

    async def configure(self, config, router, session, registry):
        self._config = config
        self._session = session
        self._registry = registry

    async def start(self):

        if 'scheduler' in self._registry:
            scheduler_plugin = self._registry.get('scheduler')
            SchedulerJobs(self._config, self._registry).add(scheduler_plugin)

        if 'github' in self._registry:
            github_plugin = self._registry.get('github')
            GitHubEndpoint(self._config).add(github_plugin)

        if 'slack' in self._registry:
            slack_plugin = self._registry.get('slack')
            SlackEndpoint(self._config).add(slack_plugin)

        self._started = True

    @property
    def started(self):
        return self._started
