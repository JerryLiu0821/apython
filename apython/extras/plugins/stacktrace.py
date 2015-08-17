"""
Installs a signal handler to print to stdout a stack trace for the currently
running test:

$ kill -USR1 `ps | grep runtest | grep -v grep | awk '{print $1}'`

This plugin does not work on Windows.
"""
import signal, sys, traceback

if hasattr(sys, 'getwindowsversion'):
    raise Exception('The stacktrace plugin does not work on Windows. Please remove plugins/stacktrace.py')

def _stacktrace(sig, stack):
    print ('SIGUSR1 received. Current stack:')
    traceback.print_stack(stack)

signal.signal(signal.SIGUSR1, _stacktrace)
