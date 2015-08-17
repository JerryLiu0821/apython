""" Basic interaction with the device. """

import android, os, re, struct, time

class Device:
    """ An instance of this object is stored in the object returned by
        android.connect():

        >>> import android
        >>> a=android.connect()
        >>> print a.device.sh('getprop ro.secure')
    """

    def __init__(self,android):
        """ PRIVATE.  """
        self.android = android

    def __del__(self):        pass    # for debugging with gc.garbage

    def android_version(self):
        """ Returns the Android version running on the device as reported by
            the ro.build.version.release system property. """
        cached_version = self.sh('getprop ro.build.version.release').strip()
        self.android_version = lambda: cached_version
        return cached_version

    def product(self):
        """ Returns the product of the device as reported by the
            ro.product.model system property. """
        cached_product = self.sh('getprop ro.product.model').strip()
        self.product = lambda: cached_product
        return cached_product

    def height(self):
        """ Returns the height of the screen (relative to the current
            orientation). """
        return self.android.internal.device.height

    def width(self):
        """ Returns the width of the screen (relative to the current
            orientation). """
        return self.android.internal.device.width

    def is_running_on_device(self):
        """ Returns True if running locally on the device; False otherwise. """
        return not isinstance(self.android.internal.transport,
                android.internal.transport_adb)

    def adb(self, command):
        """ Issues an adb command to the device associated with this object.

            Example usage:

            >>> a.device.adb('remount')     # issue 'adb remount' command
            'remount succeeded\\n'
            >>> a.device.adb('get-state')   # issue 'adb get-state' command
            'device\\n' """
        return self.android.internal.transport.adb(command)

    def id(self):
        """ Returns the serial number for the device. """
        return self.android.internal.transport.serial_number()

    def sh(self, command, input=None):
        """ Execute a command on the device through the shell. input, if 
                        specified, will be sent to the process. Returns the output of 
                        the command. """
        return self.android.internal.transport.sh(command, input)

    def ls(self, directory):
        """ Return a list of the files in a directory, or None if the
            directory does not exist. """
        output = self.sh('ls "%s/"' % directory)
        return None if re.match(
                r'%s/: (No such file or|Not a) directory[\r\n]' % directory,
                output) else output.split()

    def cat(self, file):
        """ Returns the contents of a file, or None if the file does not
            exist. """
        output = self.sh('cat "%s"' % file)
        return None if re.match(
                r'%s: (No such file or directory|invalid length)[\r\n]' % file,
                output) else output
        
    def screenshot(self,filename):
        """ Take a screen shot, saving it to 'filename' """
            try:
        stream=self.android.internal.transport.screenshot()
        version = struct.unpack('<I', stream.read(4))[0]
        if version == 16:
            # Cupcake-style, without a header
            bpp=version
            size, width, height = struct.unpack('<3I', stream.read(12))
            r_off,r_len,g_off,g_len,b_off,b_len,a_off,a_len=11,5,5,6,0,5,0,0
        elif version == 1:
            bpp,size,width,height,r_off,r_len,g_off,g_len,b_off,b_len,a_off,a_len=struct.unpack('<12I',stream.read(48))
        else:
            raise Exception('Unsupported DDMS_RAWINFO_VERSION: %d' % version)
        data=stream.read(size)
        stream.close()

        is_bgr = (r_off > b_off)

        if is_bgr and filename.lower().endswith(os.path.extsep + 'bmp'):
            DIB=struct.pack('<IiiHH6I', 40, width, -height, 1, bpp,
                    3 if bpp == 16 else 0, size, 1, 1, 0, 0)
            if bpp == 16:
                DIB += struct.pack('<3I', 0xf800, 0x7e0, 0x1f)

            BMP=struct.pack('<2sI4xI', 'BM', 14+len(DIB)+size, 14+len(DIB))

            f=open(filename, 'wb')    # exception handling
            f.write(BMP)
            f.write(DIB)
            f.write(data)
            f.close()
        else:
            try:
                """ PIL has problems parsing these BMPs, so we can't just do:

                        import PIL.ImageFile
                        p=PIL.ImageFile.Parser()
                        p.feed(BMP+DIB+data)
                        p.close().save(filename)
                """
                import PIL.Image
                modes=(    {16:('BGR;16'), 24:('BGR'), 32:('BGRX')} if is_bgr else
                        {16:('RGB;16'), 24:('RGB'), 32:('RGBX')})
                PIL.Image.fromstring('RGB', (width, height), data,
                            'raw', modes[bpp]).save(filename)
            except ImportError:
                raise Exception('a.device.screenshot requires the PIL module to save to this format on this device. Please download and install PIL from http://www.pythonware.com/products/pil/')
            except:
                print self.android.ui.screen().texts()
                raise 

    def set_lid(self,open):
        """ Simulate opening or closing the lid, used to toggle between
            landscape and portrait modes on many phones. """
        self.android.internal.device.set_lid(open)
        # give it time to take effect
        time.sleep(self.android.settings.INPUT_LID_DELAY)
        android.ui.dumpsys(self.android)    # resniff orientation

    def is_screen_on(self):
        """ Returns True if the screen is on; False if it is off. """
        return 'SCREEN_ON_BIT' in self.android.internal.transport.sh(
                'dumpsys power', android.settings.LOG_LEVEL_VERYVERBOSE)
        # Eclair+: return '00000001' in self.sh('service call power 12')

    def physical_keys(self):
        """ Returns a list of the physical keys available on the device. """
        return self.android.internal.device.physical_keys()

        def is_secure_build(self):
            """ Return whether the device is running with a secure build. """
            secure_prop = self.android.internal.transport.sh( "getprop ro.secure" ).strip()
            debuggable_prop = self.android.internal.transport.sh( "getprop ro.debuggable" ).strip()
            cached_flag = "1" in secure_prop and "0" in debuggable_prop
            self.is_secure_build = lambda: cached_flag
            return cached_flag

        def has_input_command_with_delay_option(self):
            """ Return whether the device is running with an input.jar that supports the delay option. """
            cmd_output = self.android.internal.transport.sh( "input" ).strip()
            cached_flag = "delay" in cmd_output
            self.has_input_command_with_delay_option = lambda: cached_flag
            return cached_flag

@android.register_module_callback
def _(a): a.device = Device(a)
