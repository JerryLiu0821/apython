"""
Settings for apython.

apython settings files are python scripts. Variables in all caps are loaded
into the android.settings object. The following naming convention is
recommended for settings:

(MODULE)_(SETTING NAME)

Settings are loaded from the following files in the given order:

APYTHON_INSTALL_DIRECTORY/apython.rc (this file)
APYTHON_INSTALL_DIRECTORY/local.rc
~/apython.rc            # On Windows XP, "~" translates to %USERPROFILE%
~/.apythonrc
os.environ['APYTHONRC'] # Semicolon- (on Windows) or colon- (on OS X and
                        # Unix) delimited list of settings files

Suppose the APYTHONRC environment variable is set to:

~/config/apython.rc:~/settings.rc

apython will load android.settings with the contents of the following
files, in order:

APYTHON_INSTALL_DIRECTORY/apython.rc
APYTHON_INSTALL_DIRECTORY/local.rc
~/apython.rc
~/.apythonrc
~/config/apython.rc
~/settings/apython.rc

You may also override settings for a particular connect instance:

    # load a custom settings file
    android.connect(settings='~/custom/apython.rc')
        or
    # load a custom settings dict
    android.connect(settings={'CUSTOM_SETTING':123})
        or
    # load both a custom settings file and dict
    android.connect(settings=[ '~/custom/apython.rc',
                               {'CUSTOM_SETTING':123} ])

Settings specified in this way are accessible through the android object
(a.settings instead of android.settings) and applied after the usual
settings are loaded. SUPPORT FOR INSTANCE-SPECIFIC SETTINGS IS
EXPERIMENTAL.
"""

__all__ = [ ]    # No public symbols


import android, os, sys

def _exec(f, l):
    c=open(os.path.expanduser(f),'rt').read()    # Windows or Unix line endings
    exec(compile(c, os.path.expanduser(f), 'exec'), {}, l)

def _load(to, settings):
    try:    basestring        # Python 2.x
    except:    basestring=str    # Python 3.x

    if isinstance(settings, (basestring, dict)): settings = [ settings ]
    assert isinstance(settings, (tuple, list))
    for d in settings:
        assert isinstance(d, (basestring, dict))
        if isinstance(d, basestring):
            l = dict((_,getattr(to,_)) for _ in dir(to) if _.isupper())
            try:
                _exec(d, l)
            except:
                print ('Error loading settings file: %s' % d)
                raise
            d=l
        to.__dict__.update(dict((k, d[k]) for k in d if k.isupper()))

class Settings:
    def __init__(self, settings):
        self.load(android.settings.__dict__)
        self.load(settings)

    def load(self, settings):
        """ PRIVATE """
        _load(self, settings)

def _init():
    """ PRIVATE. Used to keep the android.settings namespace clean. """
    settings = sys.modules[__name__]

    _load(settings, os.path.join(android.__path__[0], 'apython.rc'))
    _load(settings, [ f for f in [ os.path.join(android.__path__[0],'local.rc'),
                            '~/apython.rc', '~/.apythonrc' ]
                            if os.access(os.path.expanduser(f), os.F_OK) ])
    if 'APYTHONRC' in os.environ:
        _load(settings, os.environ['APYTHONRC'].split(os.pathsep))

_init()
