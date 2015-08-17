"""    Interact with screen objects

    The major class in this module is android.ui.screen. When created (with
    the android.ui.screen() method), it takes a snapshot of the current
    screen. You may then use that snapshot to find and interact with the
    various widgets on the screen. If the screen changes and you wish to
    reload the object with the latest contents of the screen, you can do so
    by calling the refresh() method.

    android.ui.screen.widget() is the main method used to find individual
    widgets on the screen. You may search for widgets by any combination of
    various attributes: id, type, text, isSelected, isFocused, isClipped.
    You may do a regular expression search on the id, type, and text fields
    by passing the output of re.compile() to android.ui.widgetspec,
    android.ui.screen.widget(), or android.ui.waitfor. You may also do a
    regular expression search on the text field by passing a search string as
    the regexp parameter.

    Typical usage:

    >>> import android
    >>> a=android.connect()
    >>> s=a.ui.screen()
    >>> s.widget(text='Use an existing account').tap()
    >>> s.refresh()

    To learn about the widgets on the screen, try starting up python in
    interactive mode:

    $ python
    >>> a=android.connect()
    >>> s=a.ui.screen()
    >>> s.w()                           # list all widgets on the screen
    >>> s.ids()                         # unique widget ids
    >>> s.texts()                       # list non-blank text fields
    >>> s.types()                       # unique widget class types
                                        # present on the screen
    >>> for w in s.widgets():           # print information about all widgets
    ...     print w
    >>> s.widget(id='saveButton').tap() # tap a button
    >>> s.refresh()                     # load new layout
"""

__all__ = [
    'UIException', 'ScreenNotFound', 'WaitforTimeout', 'WidgetNotFound',
    'widgetspec', 'windowspec', 'waitfor_hook', 'waitfor_unhook',
    'UI', 'Screen', 'Widget'
]



import android, re, time,string

TAG='ui'

def is_regexp(s): return hasattr(s,'search')    # for code clarity

class UIException(Exception):
    """ Exception from which all exceptions defined by android.ui derive. """
    def __init__(self, message):
        Exception.__init__(self, message)

class ScreenNotFound(UIException):
    """ Raised by a.ui.screen() or Screen.refresh() if the window with the
        specified title does not exist. """
    def __init__(self, title):
        self.title = title
        Exception.__init__(self, "Screen '%s' not found" % title)

class WaitforTimeout(UIException):
    """ Raised by a.ui.waitfor() and a.ui.waitfor_ex() if the specified widget
        is not found. """
    def __init__(self, title, anyof, allof, noneof, timeout, polling_interval,
                extra_hooks,screen):
        self.title=title
        self.anyof=anyof
        self.allof=allof
        self.noneof=noneof
        self.timeout=timeout
        self.polling_interval=polling_interval
        self.extra_hooks=extra_hooks
        self.screen=screen
        Exception.__init__(self,
                'waitfor: timed out (anyof=%s,allof=%s,noneof=%s,title=%s,timeout=%s,polling_interval=%s,extra_hooks=%s)' %
                (repr(anyof), repr(allof),repr(noneof), repr(title), repr(timeout), repr(polling_interval),repr(extra_hooks)))

class WidgetNotFound(UIException):
    """ Raised by a.ui.scrollto() if the specified widget is not found. """
    def __init__(self, message):
        Exception.__init__(self, message)

WIDGETSPEC_ATTRIBUTES=[
        'id', 'type', 'text', 'isClipped', 'isFocused', 'isSelected', 'tag' ]

def widgetspec(*args, **kw):
    """ Returns an object describing widget conditions for use by
        waitfor(), waitfor_ex(), widget(), or widgets().

        Valid parameters and types:
            id                  string or regular expression
            type                string or regular expression
            text                string or regular expression
            regexp              string suitable for passing to re.compile
            isClipped           True or False
            isFocused           True or False
            isSelected          True or False
            tag (EXPERIMENTAL)  string or regular expression

        Example usage:

        # TextView widgets with id='email'
        android.ui.widgetspec(id='email', type='android.widget.TextView')

        # Unclipped TextView widgets with id='email' or 'Email'
        android.ui.widgetspec(id=re.compile(r'[Ee]mail'), isClipped=False)
                type='android.widget.TextView')

        # Widgets with text matching the given regular expression
        android.ui.widgetspec(text=re.compile(
                r'^(Activity|Application) .+ is not responding\.$'))
        android.ui.widgetspec(
                regexp=r'^(Activity|Application) .+ is not responding\.$')
    """
    assert len(args) == 0, "You must explicitly indicate the attribute name. For example, android.ui.widgetspec('email') should instead be written android.ui.widgetspec(id='email')"

    if 'regexp' in kw:
        if kw['regexp'] is not None:
            assert kw.get('text') is None, "Cannot specify both 'regexp' and 'text' attributes in the same specifier"
            kw['text']=re.compile(kw['regexp'])
        del kw['regexp']
    for w in kw:
        assert w in WIDGETSPEC_ATTRIBUTES, "'%s' is not an accepted widgetspec attribute. Must be one of: %s" % (w, WIDGETSPEC_ATTRIBUTES + [ 'regexp' ] )
    return kw

def windowspec(title=None,regexp=None,package=None,activity=None):
    """ Returns an object describing a window for use by
        waitfor() or waitfor_ex()

        Regular expression searches may be specified by passing the output
        of re.compile() to the title, package, or activity parameters. """
    if regexp:
        assert title is None, "Cannot specify both 'regexp' and 'title' attributes in the same specifier"
        title=re.compile(regexp)
    return { 'title':title, 'package':package, 'activity':activity }

_waitfor_hooks = []
def waitfor_hook(hook):
    """
    Register hooks to run during waitfor and waitfor_ex. Hooks are run
    continuously in a round robin fashion in a polling loop inside
    waitfor_ex. The waitfor/waitfor_ex logic:

        1. capture screen contents
        2. if the screen matches the wait conditions, return to user
        3. otherwise, execute each hook in order and return to step 1

    This is intended to be used to handle spurious, non-error screens that
    might appear that would otherwise interfere with completion of the
    test.

    The hook registered by waitfor_hook() is prepended to the list of hooks
    to process.

    The hook is called with two arguments:
        hook(android, screen)

    Hooks should return True if waitfor_ex should stop processing the
    remaining hooks, or False if waitfor_ex should continue processing
    hooks. If a hook causes a change in the screen contents, then it
    should return True.

    Since hooks are run from within waitfor/waitfor_ex, they should not
    call waitfor or waitfor_ex.

    Sample usage:

    @android.ui.waitfor_hook
    def handle_spurious_screen(a, s):
        if s.widget(id='spurious_screen_id') is None:
            return False
        s.widget(id='button').tap()
        return True
    """
    _waitfor_hooks.insert(0, hook)
    return hook

def waitfor_unhook(hook):
    """
    Remove an entry from the list of waitfor hooks.
    """
    _waitfor_hooks.remove(hook)

@waitfor_hook
def __detect_force_close(a, s):
    # Extended by runtests.py
    regexp=re.compile(a.settings.UI_DETECT_FORCE_CLOSE_TEXT)
        textRE=re.compile(a.settings.UI_FORCE_CLOSE_BUTTON_PRESS_TEXT)
        buttonIDRE=re.compile('button[12]')
    if ( not s.widget(id='message', text=regexp) or
        not s.widget(id=buttonIDRE, text=textRE)):
        return False
    a.log.warning(TAG, 'Force close detected in: ' +
            regexp.search(s.widget(text=regexp).text()).group(1))
        #s.widget(id=buttonIDRE,text=textRE).tap()
    a.input.down()
    a.input.right()
    a.input.center()
    time.sleep(1)    # give it time to go away
    return True

@waitfor_hook
def __detect_anr(a, s):
    # Extended by runtests.py
    regexp=re.compile(a.settings.UI_DETECT_ANR_TEXT)
        textRE=re.compile(a.settings.UI_ANR_BUTTON_PRESS_TEXT)
        buttonIDRE=re.compile('button[12]')
    if ( not s.widget(id='message', text=regexp) or
        not s.widget(id=buttonIDRE, text=textRE)):
        return False
    a.log.warning(TAG, 'ANR detected in: ' +
            regexp.search(s.widget(text=regexp).text()).group(1))
    a.input.down()
    a.input.right()
    a.input.center()
    #s.widget(id=buttonIDRE,text=textRE).tap()
    time.sleep(1)    # give it time to go away
    return True

def _unlock(a, s):
    # Cupcake/Donut
    if s.widget(type='android.widget.TextView', id='lockInstructions'):
        a.input.menu()
        return True

    # Eclair
    w=s.widget(type='com.android.internal.widget.RotarySelector',
                id='rotary')
    if w:
        a.input.menu()
        a.input.drag(w.x(),w.center()[1],w.right(),w.center()[1],5)
        return True

    # Eclair/Froyo/Gingerbread
    # Don't rely on the type since one vendor uses a custom widget
    w=s.widget(id='tab_selector')
    if w:
        if w.width() > w.height():
            a.input.drag(w.x()+20,w.center()[1],w.right(),w.center()[1])
        else:
            a.input.drag(w.center()[0],w.bottom()-20,w.center()[0],w.top())
        return True

    # Ice Cream Sandwich
    w=s.widget(id='unlock_widget' )
    if w:
                if a.internal.device.rotation == 1 or a.internal.device.rotation == 3:
                a.input.drag(    w.center()[0], w.center()[1]+100,
                        w.right()-50, w.center()[1]+100)
                else:
                a.input.drag(    w.center()[0], w.center()[1],
                        w.right()-50, w.center()[1])
        return True

    # numeric pin
    if s.widget(id='pinDisplay'):
        if getattr(a.settings, 'DEVICE_PASSCODE_PIN', None) is None:
            a.log.info(TAG, 'Passcode lock screen detected, but no passcode set. Set a.settings.DEVICE_PASSCODE_PIN to unlock this screen automatically.')
            return False
        IDS={'0':'zero','1':'one','2':'two','3':'three',
                '4':'four','5':'five','6':'six','7':'seven',
                '8':'eight','9':'nine'}
        for digit in str(a.settings.DEVICE_PASSCODE_PIN):
            s.widget(id=IDS[digit]).tap()
            time.sleep(.1)
        s.widget(id='ok').tap()
        return True

    # froyo pin/password lock
    if s.widget(type='com.android.internal.policy.impl.PasswordUnlockScreen'):
        if getattr(a.settings, 'DEVICE_PASSCODE_PIN', None) is None:
            a.log.info(TAG, 'Passcode lock screen detected, but no passcode set. Set a.settings.DEVICE_PASSCODE_PIN to unlock this screen automatically.')
            return False
        time.sleep(1)
        a.input.text(str(a.settings.DEVICE_PASSCODE_PIN))
        time.sleep(.5)
        a.input.enter()
        return True

    if s.widget(type='com.android.internal.widget.LockPatternView'):
        if getattr(a.settings, 'DEVICE_PATTERN_PIN', None) is None:
            a.log.info(TAG, 'Pattern lock screen detected, but no pattern set. Set a.settings.DEVICE_PATTERN_PIN to unlock this screen automatically.')
            return False
        v=s.widget(type='com.android.internal.widget.LockPatternView')
        left=(v.width()+1)/6+v.left()
        w=v.width()/3
        top=(v.height()+1)/6+v.top()
        h=v.height()/3
        def touch(op,digit):
            digit=int(digit)
            op(left+w*((digit-1)%3),top+h*(digit/3))
        op=a.input.touch_down
        for digit in str(a.settings.DEVICE_PATTERN_PIN):
            touch(op, digit)
            op=a.input.touch_move
            time.sleep(.1)
        touch(a.input.touch_up, str(a.settings.DEVICE_PATTERN_PIN)[-1])
        return True

    return False

LOCK_SCREEN_WIDGETSPECS=[
        widgetspec(
            type='com.android.internal.policy.impl.LockPatternKeyguardView',
            id='lock_screen') ]

@waitfor_hook
def __unlock_screen(a, s):
    if not a.device.is_screen_on():
        #a.input.power()
        time.sleep(.75)

    # Check for lock screen
    if s.widget(anyof=LOCK_SCREEN_WIDGETSPECS) is None:
        return False

    result=_unlock(a, s)
    if result: time.sleep(1)
    return result

class dumpsys:
    TAG='ui.dumpsys'

    DISPLAY_RE = [ re.compile(r'DisplayWidth=(\d+) DisplayHeight=(\d+)') ]

    def __init__(self, a):
        self.a = a

        self.dumpsys = self.a.internal.transport.sh(
                # 'dumpsys window windows' is needed on ICS to retrieve the
                # device orientation
                'dumpsys window windows || dumpsys window',
                android.settings.LOG_LEVEL_VERYVERBOSE)
        product = self.a.internal.transport.sh('getprop | grep "ro.letv.product.name"')
        pn = product.split(" ")[1].strip() if product else "other"
        if pn == "[S250U]" or pn == '[S2-50F]' or pn == '[S250F]' or pn == '[S240F]'  or pn == 'other':
            self.dumpsys = self.dumpsys+ "Display: init=1920x1080 cur=1920x1080 app=1920x1080"
            sl = r'Window #\d+[:\s\r\n]+Window\{(?P<hash>[a-f\d]{7,8}) u0 (?P<title>.*)\}:?[\r\n]+(?P<attributes>(?:   .*[\r\n]+)+)'
            cm = 'mCurrentFocus=Window\{(?P<hash>\S+) u0 (?P<title>\S*)\}'
        else:
            sl = r'Window #\d+[:\s\r\n]+Window\{(?P<hash>[a-f\d]{8}) (?P<title>.*) paused=.*\}:?[\r\n]+(?P<attributes>(?:    .*[\r\n]+)+)'
            cm = 'mCurrentFocus=Window\{(?P<hash>\S+) (?P<title>\S*) \S+' 
            
        regexp=re.compile(sl, re.MULTILINE)
        self.windows=[ m.groupdict() for m in regexp.finditer(self.dumpsys) ]

        # fetch current window
        m=re.search(cm,
                self.dumpsys)
        self._focused=m.groupdict() if m else None

        for display_re in self.DISPLAY_RE:
            #m=[u.group() for u in display_re.finditer(self.dumpsys)]
            m=display_re.search(self.dumpsys)
            if m: 
                break
        else:
            raise Exception('Cannot find dimensions from dumpsys: returned %s' %
                    repr(self.dumpsys))
        self.a.internal.device.width, self.a.internal.device.height = [
                int(_) for _ in m.groups() ]

        self.a.internal.device.rotation = int(re.compile(r'  mRotation=(\d)').
                                search(self.dumpsys).group(1))

        if self._focused:
            for regexp in self.a.settings.INTERNAL_FORCE_COMPATIBILITY_MODE:
                if re.search(regexp, self._focused['title']):
                    android.log.info(self.TAG, "Forcing compatibility mode for '%s'" % self._focused['title'])
                    if not hasattr(self.a.internal.device, 'density'):
                        self.a.internal.device.density=int(self.a.internal.transport.sh('getprop ro.sf.lcd_density'))
                    self.a.internal.device.width = self.a.internal.device.width*self.a.settings.INTERNAL_COMPATIBILITY_MODE_DENSITY_DEFAULT/self.a.internal.device.density
                    self.a.internal.device.height = self.a.internal.device.height*self.a.settings.INTERNAL_COMPATIBILITY_MODE_DENSITY_DEFAULT/self.a.internal.device.density
                    break

        android.log.info(self.TAG, 'Detected screen resolution: %dx%d %s' %
                (self.a.internal.device.width, self.a.internal.device.height, repr(self.a.internal.device.rotation)))

    def __del__(self): pass

    def current_window(self):
        return self._focused['title'] if self._focused else None

    def is_input_method_up(self):
        return (re.search('mCurrentFocus=\S+ (\S+) \S+',
                self.dumpsys).group(1) != 'Keyguard' and
                re.search('mInputMethodWindow=null', self.dumpsys) is None)

    def titles(self):
        return [ _['title'] for _ in self.windows ]

    def lookup(self, title):
        if title is None:
            return [ _ for _ in self.windows
                            if _['hash'] == self._focused['hash'] ][0]

        windows = [ _ for _ in self.windows if _['title'] == title ]
        if len(windows) is 0:
            raise android.ui.ScreenNotFound(title)
        if len(windows) > 1:
            self.a.log.warning(self.TAG, "%d windows with title '%s'" % (len(windows), title))
        return windows[0]

    def hash_for_title(self, title):
        return self.lookup(title)['hash']

    def bounds_for_title(self, title):
        # XXX: ICS returns float
        return [ int(float(_)) for _ in re.compile(
                r'mShownFrame=\[([\d\.]+),([\d\.]+)\]\[([\d\.]+),([\d\.]+)\]').search(
                    self.lookup(title)['attributes']).groups() ]

class UI:
    def __init__(self, a):
        """ PRIVATE. """
        self.android = a

    def __del__(self):        pass    # for debugging with gc.garbage

    def _view_server_list_windows(self):
        data = self.android.internal.transport.view_server_query('LIST\n')
        windows = {}
        for w in data:
            hash, title = w.split(' ', 1)
            # key off hash instead of title to support same-titled screens
            windows[hash] = title
        return windows

    def windows(self):
        """ Returns a list of the titles of all the windows on the current
            device. """
        return self._view_server_list_windows().values()

    def window(self):
        """ Returns the title of the currently focused window """
        w=dumpsys(self.android).current_window()
        self.android.log.verbose(TAG, "Current window: '%s'" % w)
        return w

    def screen(self,title=None,clipping=True):
        """ Returns a Screen object for the specified window on the current
            device. If title is None, return an object for the active window.

            Raises android.ui.ScreenNotFound if title is specified and no
            window with that title is active in the system.
        """
        return Screen(self.android,title,clipping)

    def unlock(self):
        """ Check if device is in the lock screen and take it out of there if
            so. Additionally, hooks registered by android.ui.waitfor_hook are
            run. """
        self.android.log.verbose(TAG, 'unlock()')
        self.android.ui.waitfor(noneof=android.ui.windowspec('Keyguard'))

    def is_input_method_up(self):
        """ WARNING: THIS API WILL CHANGE """
        return dumpsys(self.android).is_input_method_up()

    def widgetspec(self,*args,**kw):
        """ Returns an object describing widget conditions for use by
            waitfor(), waitfor_ex(), widget(), or widgets()

            Regular expression searches may be specified by passing the output
            of re.compile() to the id, type, or text parameters. """
        return android.ui.widgetspec(*args,**kw)

    def windowspec(self,title=None,regexp=None,package=None,activity=None):
        """ Returns an object describing a window for use by
            waitfor() or waitfor_ex()

            Regular expression searches may be specified by passing the output
            of re.compile() to the title, package, or activity parameters. """
        return android.ui.windowspec(title=title,regexp=regexp,
                package=package,activity=activity)

    def waitfor(self,_=None,title=None,anyof=[],allof=[],noneof=[],
            timeout=None,polling_interval=None,extra_hooks=[],clipping=True,**kw):
        """ Waits for a widget or window to appear on the screen fitting the
            specified conditions. Returns the first matched Widget object, or
            None if only noneof is specified. Raises an
            android.ui.WaitforTimeout exception if a matching widget or window
            does not appear within 'timeout' seconds.

            If timeout is not specified, waitfor() will wait for up to
            a.settings.UI_WAITFOR_DEFAULT_TIMEOUT seconds. waitfor() is
            implemented as a polling loop, checking the screen every
            a.settings.UI_WAITFOR_DEFAULT_POLLING_INTERVAL seconds. You
            may override the polling interval by using the polling_interval
            argument (this should not normally be necessary).

            If title is specified, waitfor() will match widgetspecs against the
            window with the given title.

            waitfor hooks are called during each iteration of the polling loop.
            waitfor hooks to unlock the screen and process ANRs and Force
            Closes are registered by default by apython. Additional hooks may
            be added with the android.ui.waitfor_hook() method. Hooks
            registered with waitfor_hook() are run for every call to waitfor,
            waitfor_ex, and unlock. One time hooks may be specified by passing
            them in the extra_hooks parameter. Such hooks will be called before
            hooks registered with waitfor_hook() are called.

            There are two ways of specifying the widget to wait for:
            Simple and Complex.

            Simple: Match the values provided for id, type, text, regexp,
            isSelected, isFocused, and isClipped.

            Complex: Wait until any widgets matching anyof AND all widgets
            matching allof AND no widgets matching noneof are on the screen.
            anyof, allof, and noneof are widgetspec objects or lists of
            widgetspec objects. Sample usage:

            widgets = a.ui.waitfor(
                    anyof=[
                        a.ui.widgetspec(text='Answer'),
                        a.ui.widgetspec(id='incomingCallWidget')
                    ] )

            window = a.ui.waitfor(
                    anyof=[ a.ui.windowspec(activity=_) for _ in
                            [  'com.android.settings.DisplaySettings',
                               'com.android.settings.ApplicationSettings' ] ] )

            widgets = a.ui.waitfor(noneof=a.ui.widgetspec(text='Answer'))

            In either Simple or Complex mode, this method returns the first
            matched Widget object or a string with the name of the matched
            window. If only noneof is specified, the method will return
            None.

            Raises android.ui.WaitforTimeout if it times out.
        """
        r = self.waitfor_ex(_=_,title=title,
                anyof=anyof,allof=allof,noneof=noneof,
                timeout=timeout,polling_interval=polling_interval,
                extra_hooks=extra_hooks,clipping=clipping,**kw)
        return None if len(r) == 0 else r[0]

    def waitfor_ex(self,_=None,title=None,anyof=[],allof=[],noneof=[],
            timeout=None,polling_interval=None,extra_hooks=[],clipping=True,**kw):
        """ Identical to waitfor, except it returns the list of all
            matched Widget objects or Screen titles. """
        assert _ is None, "You must explicitly indicate the attribute name. For example, a.ui.waitfor('email') should instead be written a.ui.waitfor(id='email')"

        if timeout is None:
            timeout=self.android.settings.UI_WAITFOR_DEFAULT_TIMEOUT
        if polling_interval is None:
            polling_interval=self.android.settings.UI_WAITFOR_DEFAULT_POLLING_INTERVAL
        if not hasattr(extra_hooks,'__iter__'):
            extra_hooks=[ extra_hooks ]

        if (anyof,allof,noneof) == ([],)*3:
            # No specifiers indicates "return all widgets"
            allof=[ self.widgetspec(**kw) ]
        else:
            assert len(kw) == 0, 'Cannot pass both simple and complex widgetspecs to android.ui.waitfor'

            # Convert widgetspecs to lists
            if isinstance(anyof, dict): anyof = [ anyof ]
            if isinstance(allof, dict): allof = [ allof ]
            if isinstance(noneof, dict): noneof = [ noneof ]

        self.android.log.verbose(TAG,
                'waitfor_ex(anyof=%s,allof=%s,noneof=%s,title=%s,timeout=%s,polling_interval=%s,extra_hooks=%s)' %
                (repr(anyof), repr(allof),repr(noneof), repr(title), repr(timeout), repr(polling_interval), repr(extra_hooks)))

        global _waitfor_hooks
        s=self.android.ui.screen(title=title, clipping=clipping)
        for x in range(5):
            for hook in extra_hooks + _waitfor_hooks:
                if hook(self.android, s) is True:
                    s.refresh(clipping=clipping)
                    break
            else:
                break

        t0=time.time()
        while time.time() < t0 + timeout:
            def _(s,wspec):
                if 'title' in wspec:
                    if not hasattr(_, 'title'):    # initialize cache
                        _.title=self.android.ui.window()
                        _.package, _.activity = _.title.split('/',1) if '/' in _.title else (None, None)

                    def match_string(_for, _in):
                        return (not _for or (_for.search(_in)
                                    if is_regexp(_for) else _for == _in))

                    if (    match_string(wspec['title'], _.title) and
                            match_string(wspec['package'], _.package) and
                            match_string(wspec['activity'], _.activity)):
                        return [ _.title ]
                    return []
                return s.widgets(anyof=[ wspec ])

            fail = False
            r = []
            if not fail and allof != []:
                for wspec in allof:
                    ws=_(s,wspec)
                    fail = ws == []
                    if fail: break
                    r.extend(ws)
            if not fail and anyof != []:
                r_any = [ x for wspec in anyof for x in _(s,wspec) ]
                if len(r_any) == 0: fail = True
                r.extend(r_any)
            if not fail and noneof != []:
                fail = [ x for wspec in noneof for x in _(s,wspec) ] != []

            if not fail:
                self.android.log.verbose(TAG,
                        'waitfor_ex returned: %s' % repr(r))
                return r

            for hook in extra_hooks + _waitfor_hooks:
                if hook(self.android, s) is True:
                    break

            time.sleep(polling_interval)
            s.refresh(clipping=clipping)
        raise WaitforTimeout(title=title,anyof=anyof,allof=allof,noneof=noneof,
                    timeout=timeout,polling_interval=polling_interval,
                    extra_hooks=extra_hooks,screen=s)

    def scrollto(self,_=None,anyof=[],noneof=[],listspec=None,drag_delay=None,
            horizontal=None,steps=None,**kw):
        """
        Scroll list until first matching widget is found. anyof and noneof
        are widgetspecs or lists of widgetspecs. 'listspec' is the
        specifier or list of specifiers for the widget to be scrolled. If
        'listspec' is None, the method will search for a screen object of
        any of the types listed in a.settings.UI_SCROLLTO_LIST_TYPES.

        If there are multiple matching widgets, the method will raise an
        exception. In that case, you must pass a widgetspec in 'listspec'
        identifying the widget you wish to scroll.

        scrollto() does NOT select the object. If you want to input text
        to a field, the typical idiom is:

            a.ui.scrollto(widgetspec).tap()
            if a.ui.is_input_method_up(): a.input.back()

        Returns: The matching Widget if found. Otherwise, raises
                 android.ui.WidgetNotFound.
        """
        if listspec is None:
            listspec = [    self.widgetspec(type=x) for x in
                            self.android.settings.UI_SCROLLTO_LIST_TYPES ]

        self.android.log.verbose(TAG, 'scrollto: l=%s' % repr(listspec))

        lists=self.android.ui.waitfor_ex(anyof=listspec)
        if len(lists) == 0:
            raise Exception('No list found to scroll. Please pass a widgetspec to android.ui.scrollto identifying the list you wish to scroll.')
        if len(lists) > 1:
            raise Exception('Multiple lists found to scroll. Please pass a widgetspec to android.ui.scrollto identifying the list you wish to scroll.')

        self.android.log.verbose(TAG, 'scrollto: found list: %s'%repr(lists[0]))

        return lists[0].scrollto(_=_,anyof=anyof,noneof=noneof,
                drag_delay=drag_delay,horizontal=horizontal,**kw)

class Screen:
    def __init__(self, a, title=None, clipping=True):
        """ PRIVATE. A Screen object may be obtained by calling:

            a=android.connect()
            ...
            s=a.ui.screen()
        """
        self.android=a
        self.title=title
        self.clipping=clipping
        self.refresh(clipping=self.clipping)

    def __del__(self):        pass    # for debugging with gc.garbage

    def __repr__(self):
        return repr(self.__widgets)

    def _DUMP(self):
        d=dumpsys(self.android)
        if self.title is None and d.current_window() is None:
            # guard against no focused window condition
            return '', []
        id=d.hash_for_title(self.title)
        bounds=d.bounds_for_title(self.title)

        widgets = []
        parents = { 0:None }
        parent_offset = { 0:(bounds[0], bounds[1]) }
        dump = self.android.internal.transport.view_server_query(
                'DUMP %s\n' % id, 100)
        for l in dump:
            w = {}
            w['level'] = level = len(l) - len(l.lstrip())
            a,l = l.lstrip().split(' ', 1)
            w['fullname'] = ' '*w['level'] + a
            w['type'], w['hash'] = a.split('@')
            MAPPING = [
                    ( 'x', [ 'mLeft', 'layout:mLeft' ] ),
                    ( 'y', [ 'mTop', 'layout:mTop' ] ),
                    ( 'width', [ 'mMeasuredWidth', 'measurement:mMeasuredWidth' ] ),
                    ( 'height', [ 'mMeasuredHeight', 'measurement:mMeasuredHeight' ] ),
                    ( 'hasFocus', [ 'hasFocus()', 'focus:hasFocus()' ] ),
                    ( 'id', [ 'mID' ] ),
                    ( 'isChecked', [ 'isChecked()' ] ), # Gingerbread+ only
                    ( 'isClickable', [ 'isClickable()' ] ),
                    ( 'isEnabled', [ 'isEnabled()' ] ),
                    ( 'isFocused', [ 'isFocused()', 'focus:isFocused()' ] ),
                    ( 'isSelected', [ 'isSelected()' ] ),
                    ( 'tag', [ 'getTag()' ] ),
                    ( 'text', [ 'mText', 'text:mText' ] )
            ]
            while '=' in l:
                key,l = l.split('=', 1)
                length,l = l.split(',', 1)
                value,l = l[:int(length)], l[int(length)+1:]

                w[key]=value
            for k,v in MAPPING:
                w[k] = ''
                for _ in v:
                    if _ in w:
                        w[k] = w[_]
            try:
                w['progress1'] = int(int(w['getProgress()']) / float(w['getMax()']) * 100)
                w['progress2'] = int(int(w['getSecondaryProgress()']) / float(w['getMax()']) * 100)
            except:
                try:
                    w['progress1'] = int(int(w['progress:getProgress()']) / float(w['progress:getMax()']) * 100)
                    w['progress2'] = int(int(w['progress:getSecondaryProgress()']) / float(w['progress:getMax()']) * 100)
                except:
                    w['progress1'] = -1
                    w['progress2'] = -1
            if w['id'].startswith('id/'): w['id'] = w['id'][3:]

            """ Need to adjust based on parents' x,y,scrollx,scrolly """
            w['x'] = str(int(w['x']) + parent_offset[level][0])
            w['y'] = str(int(w['y']) + parent_offset[level][1])

            mScrollX = w['mScrollX'] if 'mScrollX' in w else w['scrolling:mScrollX']
            mScrollY = w['mScrollY'] if 'mScrollY' in w else w['scrolling:mScrollY']
            parent_offset[level+1] = (int(w['x']) - int(mScrollX),
                    int(w['y']) - int(mScrollY))

            if w['getVisibility()'] != 'VISIBLE':
                w['isVisible'],w['isClipped']=False,None
            else:
                w['isVisible'],w['isClipped']=True,False

            widget = Widget(self.android, w)
            widgets.append(widget)

            parents[level+1] = widget
            if level > 0: parents[level]._add_child(widget)
        return dump, widgets

    def refresh(self, clipping=None):
        """ Refresh this object with the current state of the screen.

            Raises android.ui.ScreenNotFound if a title was specified when
            this object was created and no window with that title is active
            in the system.
        """
        self.__dump, self.__widgets = self._DUMP()

        roots = [ w for w in self.__widgets if w._Widget__w['level'] == 0 ]
        assert len(roots) <= 1
        if roots:
            roots[0]._determine_visibility(clipping=(self.clipping
                        if clipping == None else clipping))
        self.__widgets = [ w for w in self.__widgets if w._is_visible() ]

        return self

    def __eq__(self,other):
        if type(self) is not type(other):
            return False
        return self.__dump == other.__dump

    def __ne__(self,other):
        return not self == other

    def widget(self,_=None,anyof=None,noneof=None,**kw):
        """ Return the first Widget matching the specified conditions or None
            if no matching widget is found.

            There are two ways of specifying the widget to search for:
            Simple and Complex.

            Simple: Match the values provided for id, type, text, regexp,
            isSelected, isFocused, and isClipped.

            Complex: Wait until any widgets matching anyof AND no widgets
            matching noneof are on the screen. anyof and noneof are
            widgetspec objects or lists of widgetspec objects. Sample usage:

            w = a.ui.widget( anyof=[
                    a.ui.widgetspec(text='Answer'),
                    a.ui.widgetspec(id='callAnswerSlider')
            ] )
        """
        w=self.widgets(_=_,anyof=anyof,noneof=noneof,**kw)
        return None if w == [] else w[0]

    def widgets(self,_=None,anyof=None,noneof=None,**kw):
        """ Return a list of all Widgets matching the specified conditions.  """
        assert _ is None, "You must explicitly indicate the attribute name. For example, s.widgets('email') should instead be written s.widgets(id='email')"

        if (anyof,noneof) == (None,None):
            anyof=[ self.android.ui.widgetspec(**kw) ]
        else:
            assert len(kw) == 0, 'Cannot pass both simple and complex widgetspecs to android.ui.screen.widgets'

            # Convert widgetspecs to lists
            if anyof and isinstance(anyof, dict): anyof = [ anyof ]
            if noneof and isinstance(noneof, dict): noneof = [ noneof ]

        def matches(widget,list):
            for wspec in list:
                if widget._match(wspec):
                    return True
            return False

        return [ w for w in self.__widgets if
                        (not anyof or matches(w, anyof)) and
                        (not noneof or not matches(w, noneof)) ]

    def types(self):
        """ Return a list of unique Widget types for the current Screen
            snapshot. """
        return list(set([ w.type() for w in self.__widgets ]))

    def w(self,type=None):
        """ Return a list of ( type, id ) pairs for all the widgets for the
            current Screen snapshot. """
        return [ ( w.type(), w.id() ) for w in self.__widgets
                        if type is None or w.type().find(type) >= 0 ]

    def ids(self):
        """ Return a list of unique ids for all widgets in the current Screen
            snapshot. """
        return list(set([ w.id() for w in self.__widgets ]))

    def texts(self):
        """ Return a list of ( type, id, text ) pairs for all widgets with a
            text field in the current Screen snapshot. """
        return [ ( w.type(), w.id(), w.text() ) for w in self.__widgets
                        if w.text() != '' ]

class Widget:
    """ Represents a UI object on the screen. """

    def __init__(self, a, w):
        """ PRIVATE. Widgets may be retrieved with any of the following methods:

                    android.ui.waitfor()
                    android.ui.waitfor_ex()
                    android.ui.screen().widget()
                    android.ui.screen().widgets()
        """
        self.android = a
        self.__w = w
        self.__children = []

    def __del__(self):        pass    # for debugging with gc.garbage

    def __repr__(self):
        return repr(self.__w)

    def type(self):            return self.__w['type']
    def id(self):            return self.__w['id']

    def has_focus(self):    return self.__w['hasFocus'] == 'true'
    def is_clickable(self):    return self.__w['isClickable'] == 'true'
    def is_enabled(self):    return self.__w['isEnabled'] == 'true'
    def is_focused(self):    return self.__w['isFocused'] == 'true'
    def is_selected(self):    return self.__w['isSelected'] == 'true'
    def text(self):            return self.__w['text']
    def progress(self):
        """ EXPERIMENTAL. Returns primary and secondary progress percentages
            for a ProgressBar as a tuple. """
        return (int(self.__w['progress1']), int(self.__w['progress2']))

    def tag(self):
        """ EXPERIMENTAL. Returns view-specific data. """
        return self.__w['tag']

    def x(self):            return int(self.__w['x'])
    def y(self):            return int(self.__w['y'])
    def width(self):        return int(self.__w['width'])
    def height(self):        return int(self.__w['height'])
    def left(self):            return self.x()
    def top(self):            return self.y()
    def right(self):        return self.x() + self.width() - 1
    def bottom(self):        return self.y() + self.height() - 1

    def pos(self):            return ( self.x(), self.y() )
    def size(self):            return ( self.width(), self.height() )
    def center(self):
        return (    self.x() + self.width() / 2,
                    self.y() + self.height() / 2 )

    def children(self):
        """ EXPERIMENTAL: Direct descendents of this widget in the widget tree. """

        """ We don't store the parent of the widget because that would
            interact poorly with Python's GC. If we used a weakref, the
            parent field could be invalidated when the Screen object goes
            out of scope (e.g. upon returning from android.ui.waitfor())
            and so could only be relied upon in specific circumstances.
            If we used an ordinary reference, there would be looped
            references and the widgets would never be cleaned up. We can
            either store ordinary references to all the children or all
            the parents. I've chosen all the children in the hopes that
            it satisfies the majority of use cases.
        """
        return self.__children

    def parent(self, screen):
        """ EXPERIMENTAL: Parent of this widget in the widget tree. """
        assert self in screen._Screen__widgets
        for w in screen._Screen__widgets:
            if self in w.__children:
                return w
        return None

    def _is_visible(self):
        return self.__w['isVisible']

     def is_clipped(self):    return self.__w['isClipped']

    def _add_child(self,w):
        self.__children.append(w)

    def _match(self,widgetspec):
        def match_string(_for, _in):
            return (_for.search(_in) if is_regexp(_for) else _for == _in)
        def match_bool(_for, _in):
            return (_in if isinstance(_in, bool) else _in == 'true') == _for
        for k in widgetspec:
            if k.startswith('is'):
                if not match_bool(widgetspec[k], self.__w[k]): return False
            else:
                if not match_string(widgetspec[k], self.__w[k]): return False
        return True

    def tap(self, tap_delay=None):
        """ Simulate a user touching the center of the Widget. """
        self.android.input.tap(self.x() + self.width() / 2,
                self.y() + self.height() / 2, tap_delay)

    def dragto(self,x,y,steps=3,skip_down=False,skip_up=False,drag_delay=None):
        """ Simulate a user dragging from the center of the Widget to (x,y) """
        (x0,y0) = self.center()
        self.android.input.drag(x0,y0,x,y,steps,skip_down,drag_delay)

    def _is_horizontal_scroller(self):
        for wspec in self.android.settings.UI_SCROLLTO_HORIZONTAL:
            if isinstance(wspec, basestring):
                if self.type() == wspec:
                    return True
            if self._match(wspec):
                return True
        return False

    def scrollby(self,pages,drag_delay=None,horizontal=None,steps=None):
        """ Scroll the widget by a given number of pages. Positive numbers
            scroll down, negative numbers scroll up. """
        if horizontal is None:
            horizontal = self._is_horizontal_scroller()
        s=self.android.ui.screen()
        self._scrollby(pages=pages,drag_delay=drag_delay,horizontal=horizontal,
                steps=steps)
        t=self.android.ui.screen()
        return s != t

    def _scrollby(self,pages,drag_delay,horizontal,steps):
        assert pages is not None

        if steps is None: steps=self.android.settings.UI_SCROLLBY_STEPS

        # If it's too close to the edge, touch can be interpreted by the
        # framework as a sloppy touch to an adjacent widget
        # XXX: Is this constant across devices? May be dependent on density.
        delta = self.android.settings.UI_SCROLLBY_SLOP

        def __vscrollby(pages):
            y0 = (self.top() + delta) if pages < 0 else (self.bottom() - delta)
            y1 = int(y0 - self.height()*pages)

            # clamp to visible screen
            y0 = max(0, min(self.android.device.height(), y0))
            y1 = max(0, min(self.android.device.height(), y1))

            x=self.center()[0]
            self.android.input.drag(x,y0,x,y1,steps,drag_delay=drag_delay)

        def __hscrollby(pages):
            x0 = (self.left() + delta) if pages < 0 else (self.right() - delta)
            x1 = int(x0 - self.width()*pages)

            # clamp to visible screen
            x0 = max(0, min(self.android.device.width(), x0))
            x1 = max(0, min(self.android.device.width(), x1))

            y=self.center()[1]
            self.android.input.drag(x0,y,x1,y,steps,drag_delay=drag_delay)

        __scrollby = __hscrollby if horizontal else __vscrollby

        while abs(pages) > 1:
            __scrollby(1 if pages > 0 else 0)
            pages -= 1
        if pages != 0: __scrollby(pages)

    def pageup(self,drag_delay=None,steps=None):
        """ Scroll the widget up by one page. """
        return self.scrollby(pages=-1,drag_delay=drag_delay,horizontal=False,
                steps=steps)

    def pagedown(self,drag_delay=None,steps=None):
        """ Scroll the widget down by one page. """
        return self.scrollby(pages=1,drag_delay=drag_delay,horizontal=False,
                steps=steps)

    def pageleft(self,drag_delay=None,steps=None):
        """ Flick the widget to the left by one screen. """
        return self.scrollby(pages=-1,drag_delay=drag_delay,horizontal=True,
                steps=steps)

    def pageright(self,drag_delay=None,steps=None):
        """ Flick the widget to the right by one screen. """
        return self.scrollby(pages=1,drag_delay=drag_delay,horizontal=True,
                steps=steps)

    def scrollto(self,_=None,anyof=[],noneof=[],drag_delay=None,steps=None,
                horizontal=None,**kw):
        assert _ is None, "You must explicitly indicate the attribute name. For example, w.scrollto('email') should instead be written w.scrollto(id='email')"

        if (anyof,noneof) == ([],[]):
            # No specifiers indicates "return first matching widget"
            anyof=[ android.ui.widgetspec(**kw) ]
        else:
            assert len(kw) == 0, 'Cannot pass both simple and complex widgetspecs to android.ui.widget.scrollto'

            # Convert widgetspecs to lists
            if isinstance(anyof, dict): anyof = [ anyof ]
            if isinstance(noneof, dict): noneof = [ noneof ]

        if    (    any([ _.get('isSelected',None) for _ in anyof ]) or
                any([ _.get('isSelected',None) for _ in noneof ])):
            raise Exception('scrollto(): isSelected should not be set to True in specifiers')

        assert (anyof,noneof) != ([],[])

        self.android.log.verbose(TAG,
                'scrollto: widget=%s, anyof=%s, noneof=%s' %
                (repr(self), repr(anyof), repr(noneof)))

        if horizontal is None:
            horizontal=self._is_horizontal_scroller()

        s=self.android.ui.screen()

        # Go to the bottom, looking for widgets as we go
        for _ in range(self.android.settings.UI_SCROLLTO_PAGE_LIMIT):
            w=s.widget(anyof=anyof,noneof=noneof)
            if w is not None:
                self.android.log.verbose(TAG,
                        'scrollto: widget found: %s' % repr(w))
                return w
            self.android.log.verbose(TAG,
                    'scrollto: widget not found. moving ' +
                    'left.' if horizontal else 'down.')
            self._scrollby(pages=1,drag_delay=drag_delay,horizontal=horizontal,
                    steps=steps)
            time.sleep(self.android.settings.UI_SCROLLTO_PAGING_DELAY)
            t=s
            s=self.android.ui.screen()
            if s == t:
                break

        # Go to the top, looking for widgets as we go
        for _ in range(self.android.settings.UI_SCROLLTO_PAGE_LIMIT):
            w=s.widget(anyof=anyof,noneof=noneof)
            if w is not None:
                self.android.log.verbose(TAG,
                        'scrollto: widget found: %s' % repr(w))
                return w
            self.android.log.verbose(TAG,
                    'scrollto: widget not found. moving ' +
                    'right.' if horizontal else 'up.')
            self._scrollby(pages=-1,drag_delay=drag_delay,horizontal=horizontal,
                    steps=steps)
            time.sleep(self.android.settings.UI_SCROLLTO_PAGING_DELAY)
            t=s
            s=self.android.ui.screen()
            if s == t:
                break

        self.android.log.verbose(TAG, 'scrollto: widget not found')
        raise WidgetNotFound('scrollto: widget not found')

    def capture(self, format='png'):
        """ EXPERIMENTAL: Retrieve a bitmap containing the contents of the
            widget. Currently only works on widgets in the focused window. """
        png=self.android.internal.transport.view_server_capture(
                'ffffffff', self.type(), self.__w['hash'])
        # XXX: support non-ffffffff

        if format.lower() == 'png':
            return png

        if format.lower() == 'pil':
            try:
                from StringIO import StringIO as BytesIO
            except ImportError:
                from io import BytesIO        # Py3K
            try:
                import PIL.Image
                return PIL.Image.open(BytesIO(png))
            except ImportError:
                raise Exception('a.ui.widget.capture requires the PIL module to save to export in PIL format. Please download and install PIL from http://www.pythonware.com/products/pil/')

        raise Exception("Unknown format (%s). Must be 'pil' or 'png'." % format)

    def _determine_visibility(self,parent=None,clipping=True):
        if parent and clipping == True:
            left, top, right, bottom = (    self.left(), self.top(),
                                            self.right(), self.bottom())

            def w2str(w):
                return '%s/%s [%s,%s,%s,%s]' % (w.type(), w.id(),
                        w.left(), w.top(), w.right(), w.bottom())
            def w2str_self():
                return '%s/%s [%s,%s,%s,%s]' % (self.type(), self.id(),
                        left, top, right, bottom)
            def log_clipped(where,by,w):
                self.android.log.veryverbose(TAG,
                        'widget %s clipped %s by %s %s' %
                                (w2str_self(), where, by, w2str(w)))
            if (    not parent._is_visible() or
                    self.width() == 0 or self.height() == 0 or
                    left > parent.right() or right < parent.left() or
                    top > parent.bottom() or bottom < parent.top()):
                log_clipped('completely','parent',parent)

                self.__w['isVisible'],self.__w['isClipped'] = False, None
            else:
                # clip to parent
                if left < parent.left():
                    log_clipped('on left','parent',parent)
                    left, self.__w['isClipped'] = parent.left(), True
                if right > parent.right():
                    log_clipped('on right','parent',parent)
                    right, self.__w['isClipped'] = parent.right(), True
                if top < parent.top():
                    log_clipped('on top','parent',parent)
                    top, self.__w['isClipped'] = parent.top(), True
                if bottom > parent.bottom():
                    log_clipped('on bottom','parent',parent)
                    bottom, self.__w['isClipped'] = parent.bottom(), True

                # Clip against siblings. Siblings later in the list are drawn
                # on top of this one.
                siblings=parent.__children[parent.__children.index(self)+1:]
                for sibling in siblings:
                    if not sibling._is_visible():
                        continue

                    if (    top > sibling.bottom() or bottom < sibling.top() or
                            left > sibling.right() or right < sibling.left()):
                        continue        # widgets are disjoint

                    if (sibling.top() <= top < bottom <= sibling.bottom() and
                        sibling.left() <= left < right <= sibling.right()):
                        log_clipped('completely','sibling',sibling)
                        continue        # obscured by sibling

                    # Only handle the cases where area(self) - area(sibling)
                    # is rectangular.
                    if (    left < sibling.left() < right <= sibling.right() and
                            sibling.top() <= top < bottom <= sibling.bottom()):
                        log_clipped('on right','sibling',sibling)
                        right, self.__w['isClipped'] = sibling.left()-1, True

                    elif (    sibling.left() <= left < sibling.right() < right and
                            sibling.top() <= top < bottom <= sibling.bottom()):
                        log_clipped('on left','sibling',sibling)
                        left, self.__w['isClipped'] = sibling.right()+1, True

                    elif (    top < sibling.top() < bottom <= sibling.bottom() and
                            sibling.left() <= left < right <= sibling.right()):
                        log_clipped('on bottom','sibling',sibling)
                        bottom, self.__w['isClipped'] = sibling.top()-1, True

                    elif (    sibling.top() <= top < sibling.bottom() < bottom and
                            sibling.left() <= left < right <= sibling.right()):
                        log_clipped('on top','sibling',sibling)
                        top, self.__w['isClipped'] = sibling.bottom()+1, True

                if self.__w['isClipped']:
                    self.__w['x']=str(left)
                    self.__w['y']=str(top)
                    self.__w['width']=str(right - left + 1)
                    self.__w['height']=str(bottom - top + 1)

                    self.android.log.veryverbose(TAG,
                            'widget is now: %s' % w2str(self)) 
        [ w._determine_visibility(self, clipping) for w in self.__children ]

@android.register_module_callback
def _(a):
    a.ui = UI(a)

    # Sniff screen dimensions and orientation so DPAD input is correct at
    # apython start up.
    dumpsys(a)
