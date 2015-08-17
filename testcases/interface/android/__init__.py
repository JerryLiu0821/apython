"""
A package for interacting with Android

android.connect() returns an interface to interacting with a specific
attached device.
"""

BUILDTIME = '20120711.181200'

import android.settings, android.internal
def register_module_callback(callback):
    android.internal.register_module_callback(callback)

for _ in android.settings.APYTHON_AUTOIMPORT:
	__import__(_)

# Site-specific customizations
import os, sys
if os.access(os.path.join(os.path.dirname(sys.modules[__name__].__file__),
		'local.py'), os.R_OK):
	import android.local

def register_connect_hook(callback):
	""" EXPERIMENTAL """
	raise Exception('android.register_connect_hook may only be used when tests are run through runtests.py')

_connection_recovery_hooks = [ ]
def register_connection_recovery_hook(callback):
	""" If the connection to the device is interrupted and reestablished,
		the callback will be called after the connection has been
		recovered. This is only meaningful if the setting
		INTERNAL_RETRY_ON_CONNECTION_ERROR is True
	"""
	_connection_recovery_hooks.append(callback)

_connection_failure_hooks = [ ]
def register_connection_failure_hook( failure, callback ):
    """
        If the connection to the device has been interrupted
        due to a particular type of failure, a mechanism is provide to
        attempt failure recovery by calling the provide callback.
    """
    _connection_failure_hooks.append( (failure, callback ) )
	
def connect(id=None, settings=[]):
	"""
	Returns an "android" object for interacting with a specific attached
	device. If run locally on a device, connect() will return an object for
	interacting with that device. If run remotely, id may be used to
	specify a device by serial number (as reported by 'adb devices'). If
	id is not specified and only one device is attached to the host, then
	apython will connect to that device. You may also specify a default
	device for apython to connect to by specifying its serial number in
	the environment variable ANDROID_SERIAL.

	The returned object has several important interfaces: device, home,
	input, log, settings, and ui. For more details:

	>>> import android
	>>> help(android.device)
	>>> help(android.home)
	>>> help(android.input)
	>>> help(android.log)
	>>> help(android.settings)
	>>> help(android.ui)

	or consult the documentation in the doc/ directory.
	"""
	return android.internal.connect(id,settings)
