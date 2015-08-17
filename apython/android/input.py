"""    Send keyboard and touchscreen events to the device.

    An instance of this object is stored in the object returned by
    android.connect():

    >>> import android
    >>> a=android.connect()
    >>> a.input.text('sample text')

    Commonly-used APIs:

    >>> a.input.text(s)                 # 'type' text 's' on device
    >>> a.input.tap(x,y)                # send touchscreen tap event
    >>> a.input.drag(x1,y1,x2,y2,steps) # simulate drag from (x1,y1) to (x2,y2)
                                        # with 'steps' intermediate move events
    >>> a.input.up()                    # send DPAD UP key event
    >>> a.input.right()                 # send DPAD RIGHT key event
    >>> a.input.down()                  # send DPAD DOWN key event
    >>> a.input.left()                  # send DPAD LEFT key event
    >>> a.input.center()                # send DPAD CENTER key event
    >>> a.input.menu()                  # send MENU key event

    Less commonly-used APIs, for simulating long key presses or touch events:

    >>> a.input.key_down(name)          # send key down event only for key
                                        # 'name'
    >>> a.input.key_up(name)            # send key up event only for key 'name'
    >>> a.input.touch_down(x,y)         # send touch down event only
    >>> a.input.touch_up(x,y)           # send touch up event only
    >>> a.input.touch_move(x,y)         # send touch move event only
"""

import time

# Basic primitives

TAG='input'

class Input:
    def __init__(self,a):
        """ PRIVATE. """
        self.android = a

    def __del__(self):        pass    # for debugging with gc.garbage

    def key(self, name, n=1):
        """ Raw API to send key 'name' to the device 'n' times. 'name'
            is a string defined in the device keymap. Available keys
            are listed in a.input.keycodes(). """
        for x in range(n):
            self.android.internal.device.key(name)

    def key_down(self, name):    self.android.internal.device.key_down(name)
    def key_up(self, name):        self.android.internal.device.key_up(name)

    def text(self, s, delay=None):    self.android.internal.device.text(s)

    def touch_down(self, x, y):    self.android.internal.device.touch_down(x, y)
    def touch_move(self, x, y):    self.android.internal.device.touch_move(x, y)
    def touch_up(self, x, y):    self.android.internal.device.touch_up(x, y)
    def tap(self, x, y, tap_delay=None):
        if tap_delay:
            self.touch_down(x, y)
            time.sleep(tap_delay)
            self.touch_up(x, y)
        else:
            self.android.internal.device.touch(x, y)

    def drag(self, x1, y1, x2, y2, steps=3, skip_down=False, skip_up=False,
            drag_delay=None):
        self.android.internal.device.drag(
                x1,y1,x2,y2,steps,skip_down,skip_up,drag_delay)

    def home(self,n=1):                self.key('HOME',n)
    def back(self, n=1):        self.key('BACK',n)

    def _dpad(self, dir, n=1):
        _=[ 'DPAD_UP', 'DPAD_RIGHT', 'DPAD_DOWN', 'DPAD_LEFT' ]
        self.key(_[(_.index(dir)+self.android.internal.device.rotation) % 4], n)

    def up(self, n=1):            self._dpad('DPAD_UP', n)
    def down(self, n=1):        self._dpad('DPAD_DOWN', n)
    def left(self, n=1):        self._dpad('DPAD_LEFT', n)
    def right(self, n=1):        self._dpad('DPAD_RIGHT', n)

    def center(self, n=1):        self.key('DPAD_CENTER',n)
    def volume_up(self, n=1):    self.key('VOLUME_UP',n)
    def volume_down(self, n=1):    self.key('VOLUME_DOWN',n)
    def channel_up(self, n=1):    self.key('CHANNEL_UP',n)
    def channel_down(self, n=1):    self.key('CHANNEL_DOWN',n)
    def power(self):            self.key('POWER')
    def camera(self):            self.key('CAMERA')
    def focus(self):            self.key('FOCUS')
    def alt_left(self):            self.key('ALT_LEFT')
    def alt_right(self):        self.key('ALT_RIGHT')
    def shift_left(self):        self.key('SHIFT_LEFT')
    def shift_right(self):        self.key('SHIFT_RIGHT')
    def sym(self):                self.key('SYM')
    def delete(self, n=1):        self.key('DEL',n)
    def menu(self, n=1):        self.key('MENU',n)
    def search(self):            self.key('SEARCH')
    def enter(self):            self.key('ENTER')

    def keycodes(self):
        return self.android.internal.device.keymap.keys()

import android
@android.register_module_callback
def _(a): a.input = Input(a)
