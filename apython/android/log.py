import android, os

def _log(level, tag, message, html=None):
    """ PRIVATE. """
    if android.settings.LOG_LEVEL_STDOUT >= level:
        print ('\n'.join( [ '%d [%s] %s' % (level, tag, m)
                for m in message.splitlines() ]))

def error(tag, message, html=None):
    """ Log an error level message """
    _log(android.settings.LOG_LEVEL_ERROR, tag, message, html)

def warning(tag, message, html=None):
    """ Log a warning level message """
    _log(android.settings.LOG_LEVEL_WARNING, tag, message, html)

def info(tag, message, html=None):
    """ Log an info level message """
    _log(android.settings.LOG_LEVEL_INFO, tag, message, html)

def debug(tag, message, html=None):
    """ Log a debug level message """
    _log(android.settings.LOG_LEVEL_DEBUG, tag, message, html)

def verbose(tag, message, html=None):
    """ Log a verbose level message """
    _log(android.settings.LOG_LEVEL_VERBOSE, tag, message, html)

def veryverbose(tag, message, html=None):
    """ PRIVATE. Log a veryverbose level message """
    _log(android.settings.LOG_LEVEL_VERYVERBOSE, tag, message, html)

def report_directory():
    """ EXPERIMENTAL: Relative to initial directory.
        For example: 'report.20100927_120229' """
    return '.'

def logs_directory():
    """ EXPERIMENTAL: Relative to a.log.report_directory().
        For example: 'logs/00002' """
    return '.'

def report(html=None, xml=None):
    """ EXPERIMENTAL: Log text to report files (index.html, report.xml). """
    pass

def log_report(html=None, xml=None):
    """ DEPRECATED """
    return report(html,xml)

def strip_report_directory(d):
    """ EXPERIMENTAL: Takes a filename returned by log_filename and returns
        a path relative to android.log.report_directory() This is useful when
        writing log locations to index.html and report.xml.

        For example:

            'report.20100927_120229/logs/00002/log.txt' => 'logs/00002/log.txt'
    """
    r=report_directory()
    assert d.startswith(r + os.sep)
    return d[len(r)+1:]

class Log:
    def __init__(self, a):
        """ PRIVATE. Access via the android object: a.log """
        self.android = a

    def __del__(self): pass    # for debugging with gc.garbage()

    def _format(self, message):
        if self.android and self.android.device.id():
            return '\n'.join( [ '%s: %s' % (self.android.device.id(), m)
                    for m in message.splitlines() ] )
        return message

    def error(self, tag, message, html=None):
        """ Log an error level message (with the device id, if appropriate) """
        android.log.error(tag, self._format(message), html)

    def warning(self, tag, message, html=None):
        """ Log a warning level message (with the device id, if appropriate) """
        android.log.warning(tag, self._format(message), html)

    def info(self, tag, message, html=None):
        """ Log an info level message (with the device id, if appropriate) """
        android.log.info(tag, self._format(message), html)

    def debug(self, tag, message, html=None):
        """ Log a debug level message (with the device id, if appropriate) """
        android.log.debug(tag, self._format(message), html)

    def verbose(self, tag, message, html=None):
        """ Log a verbose level message (with the device id, if appropriate) """
        android.log.verbose(tag, self._format(message), html)

    def veryverbose(self, tag, message, html=None):
        """ PRIVATE. Log a veryverbose level message (with the device id,
            if appropriate) """
        android.log.veryverbose(tag, self._format(message), html)

    def log_filename(self, template):
        """ EXPERIMENTAL: THIS API MAY CHANGE. """
        return os.path.join(android.log.report_directory(),
                android.log.logs_directory(), template)

@android.register_module_callback
def _(a): a.log = Log(a)
