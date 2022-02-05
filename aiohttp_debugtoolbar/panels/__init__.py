from .headers import HeaderDebugPanel
from .logger import LoggingPanel
from .middlewares import MiddlewaresDebugPanel
from .performance import PerformanceDebugPanel
from .request_vars import RequestVarsDebugPanel
from .routes import RoutesDebugPanel
from .settings import SettingsDebugPanel
from .traceback import TracebackPanel
from .versions import VersionDebugPanel

# flake8
(
    HeaderDebugPanel,
    PerformanceDebugPanel,
    SettingsDebugPanel,
    TracebackPanel,
    MiddlewaresDebugPanel,
    VersionDebugPanel,
    RoutesDebugPanel,
    RequestVarsDebugPanel,
    LoggingPanel,
)
