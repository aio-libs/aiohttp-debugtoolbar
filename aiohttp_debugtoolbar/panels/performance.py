try:
    import cProfile as profile
except ImportError:  # pragma: no cover
    try:
        import profile
    except ImportError:  # pragma: no cover
        profile = None
try:
    import resource
except ImportError:  # pragma: no cover
    resource = None  # Will fail on Win32 systems
try:
    import pstats
except ImportError:  # pragma: no cover
    pstats = None  # will fail on braindead Debian systems that package pstats
    # separately from python for god-knows-what-reason


import time

from .base import DebugPanel
from ..utils import format_fname


__all__ = ['PerformanceDebugPanel']


class PerformanceDebugPanel(DebugPanel):
    """
    Panel that looks at the performance of a request.

    It will display the time a request took and, optionally, the
    cProfile output.
    """
    name = 'Performance'
    user_activate = True
    stats = None
    function_calls = None
    has_resource = bool(resource)
    has_content = bool(pstats and profile)
    template = 'performance.jinja2'
    title = 'Performance'
    nav_title = title

    def __init__(self, request):
        super().__init__(request)
        if profile is not None:
            self.profiler = profile.Profile()

    def _wrap_timer_handler(self, handler):
        if self.has_resource:
            async def resource_timer_handler(request):
                _start_time = time.time()
                self._start_rusage = resource.getrusage(resource.RUSAGE_SELF)
                try:
                    result = await handler(request)
                except BaseException:
                    raise
                finally:
                    self._end_rusage = resource.getrusage(resource.RUSAGE_SELF)
                    self.total_time = (time.time() - _start_time) * 1000

                return result

            return resource_timer_handler

        async def noresource_timer_handler(request):
            _start_time = time.time()
            try:
                result = await handler(request)
            except BaseException:
                raise
            finally:
                self.total_time = (time.time() - _start_time) * 1000
            return result

        return noresource_timer_handler

    def _wrap_profile_handler(self, handler):
        if not self.is_active:
            return handler

        async def profile_handler(request):
            try:
                self.profiler.enable()
                try:
                    result = await handler(request)
                finally:
                    self.profiler.disable()
            except BaseException:
                raise
            finally:
                stats = pstats.Stats(self.profiler)
                function_calls = []
                flist = stats.sort_stats('cumulative').fcn_list
                for func in flist:
                    current = {}
                    info = stats.stats[func]

                    # Number of calls
                    if info[0] != info[1]:
                        current['ncalls'] = '%d/%d' % (info[1], info[0])
                    else:
                        current['ncalls'] = info[1]

                    # Total time
                    current['tottime'] = info[2] * 1000

                    # Quotient of total time divided by number of calls
                    if info[1]:
                        current['percall'] = info[2] * 1000 / info[1]
                    else:
                        current['percall'] = 0

                    # Cumulative time
                    current['cumtime'] = info[3] * 1000

                    # Quotient of the cumulative time divided by the number
                    # of primitive calls.
                    if info[0]:
                        current['percall_cum'] = info[3] * 1000 / info[0]
                    else:
                        current['percall_cum'] = 0

                    # Filename
                    filename = pstats.func_std_string(func)
                    current['filename_long'] = filename
                    current['filename'] = format_fname(filename)
                    function_calls.append(current)

                self.stats = stats
                self.function_calls = function_calls

            return result

        return profile_handler

    def wrap_handler(self, handler, context_switcher):
        handler = self._wrap_profile_handler(handler)
        handler = self._wrap_timer_handler(handler)
        return handler

    @property
    def nav_subtitle(self):
        return '%0.2fms' % (self.total_time)

    def _elapsed_ru(self, name):
        return getattr(self._end_rusage, name) - getattr(self._start_rusage,
                                                         name)

    async def process_response(self, response):
        vars = {'timing_rows': None, 'stats': None, 'function_calls': []}
        if self.has_resource:
            utime = 1000 * self._elapsed_ru('ru_utime')
            stime = 1000 * self._elapsed_ru('ru_stime')
            vcsw = self._elapsed_ru('ru_nvcsw')
            ivcsw = self._elapsed_ru('ru_nivcsw')
            # minflt = self._elapsed_ru('ru_minflt')
            # majflt = self._elapsed_ru('ru_majflt')

            # these are documented as not meaningful under Linux.  If you're
            # running BSD # feel free to enable them, and add any others that
            # I hadn't gotten to before I noticed that I was getting nothing
            # but zeroes and that the docs agreed. :-(
            #
            #            blkin = self._elapsed_ru('ru_inblock')
            #            blkout = self._elapsed_ru('ru_oublock')
            #            swap = self._elapsed_ru('ru_nswap')
            #            rss = self._end_rusage.ru_maxrss
            #            srss = self._end_rusage.ru_ixrss
            #            urss = self._end_rusage.ru_idrss
            #            usrss = self._end_rusage.ru_isrss

            # TODO l10n on values
            rows = (
                ('User CPU time', '%0.3f msec' % utime),
                ('System CPU time', '%0.3f msec' % stime),
                ('Total CPU time', '%0.3f msec' % (utime + stime)),
                ('Elapsed time', '%0.3f msec' % self.total_time),
                ('Context switches', '%d voluntary, %d involuntary' % (
                    vcsw, ivcsw)),
                # (_('Memory use'), '%d max RSS, %d shared, %d unshared' % (
                # rss, srss, urss + usrss)),
                # (_('Page faults'), '%d no i/o, %d requiring i/o' % (
                # minflt, majflt)),
                # (_('Disk operations'), '%d in, %d out, %d swapout' % (
                # blkin, blkout, swap)),
            )
            vars['timing_rows'] = rows
        if self.is_active:
            vars['stats'] = self.stats
            vars['function_calls'] = self.function_calls
        self.data = vars
