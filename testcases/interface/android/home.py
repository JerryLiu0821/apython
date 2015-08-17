""" Basic interaction with the home screen. """


import android, re

TAG='home'

class Home:
	""" An instance of this object is stored in the object returned by
		android.connect():

		>>> import android
		>>> a=android.connect()
		>>> a.home.menu_item('Dialer')
	"""

	def __init__(self,android):
		""" PRIVATE.  """
		self.android = android

		self._HOME_TITLES = [
				'com.android.launcher/com.android.launcher.Launcher',
				'com.android.launcher/com.android.launcher2.Launcher',
				'com.android.launcher/com.android.launcher2.Launch'
		]

		# com.android.launcher.AllAppsGridView
		# com.android.launcher2.AllAppsView
		# com.android.launcher2.AllApps2D
		# com.android.launcher2.AllApps3D
		# com.android.launcher2.PagedViewIcon	# Honeycomb, Ice Cream Sandwich
		self._TRAY_SPEC = [
				android.ui.widgetspec(type=re.compile(
						r'^com.android.launcher\d?.AllApps(2D|3D|GridView|View)$')),
				android.ui.widgetspec(
						type='com.android.launcher2.PagedViewIcon')
		]

		# com.android.launcher2.AllApps3D
		self._TRAY_SPEC_3D = [
				android.ui.widgetspec(type='com.android.launcher2.AllApps3D') ]

		# com.android.launcher.HandleView
		# com.android.launcher2.HandleView
		self._HANDLE_SPEC = [
				android.ui.widgetspec(type=re.compile(
						r'com.android.launcher\d?.HandleView')),
				# Honeycomb
				android.ui.widgetspec(type='android.widget.TextView',
						id='all_apps_button'),
				# Ice Cream Sandwich
				android.ui.widgetspec(type='com.android.launcher2.Hotseat',
						id='hotseat'),
                                android.ui.widgetspec(type='com.android.launcher2.HolographicImageView',
                                                id='all_apps_button')
		]

	def __del__(self):		pass	# for debugging with gc.garbage

	def home(self,open_tray=False):
		""" Go to the home screen, unlocking the device if needed. """
		self.android.log.debug(TAG,
				'Go to the home screen (open_tray=%s)' % repr(open_tray))

		# Make sure screen is unlocked, handle force closes, ANRs
		self.android.ui.unlock()

		if self.android.ui.window() not in self._HOME_TITLES:
			self.android.log.verbose(TAG, 'Pressing HOME key')
			self.android.input.home()
			self.android.log.verbose(TAG, 'Waiting for home screen')
			self.android.ui.waitfor(anyof=[ android.ui.windowspec(_)
					for _ in self._HOME_TITLES ], timeout=20)

		s=self.android.ui.screen()
		if (s.widget(anyof=self._TRAY_SPEC) is not None) != open_tray:
			if open_tray:
				self.android.log.verbose(TAG, 'Opening app tray')
				s.widget(anyof=self._HANDLE_SPEC).tap()
				self.android.ui.waitfor(anyof=self._TRAY_SPEC)
			else:
				self.android.log.verbose(TAG, 'Closing app tray')
				self.android.input.back()
				self.android.ui.waitfor(noneof=self._TRAY_SPEC)

	def _widgetspec_for(self, app):
		return [	android.ui.widgetspec(id='name',text=app),
					# Honeycomb
					android.ui.widgetspec(
							type='com.android.launcher2.PagedViewIcon',
							tag=('ApplicationInfo(title=%s)' % app)) ]

	def menu_item(self,app,do_tap=True):
		""" Go to the home screen and launch 'app' from the app tray.
			This API only works with 2D versions of the application tray.  """
		self.android.log.debug(TAG, "Launching '%s' from the app tray" % app)
		self.home(True)

		if self.android.ui.screen().widget(anyof=self._TRAY_SPEC_3D):
			raise Exception('android.home.menu_item() does not work with the 3D application tray')

		w = self.android.ui.waitfor(anyof=self._TRAY_SPEC).scrollto(
				anyof=self._widgetspec_for(app), drag_delay=2)
                if do_tap:
                    w.tap()
		    self.android.ui.waitfor(noneof=self._TRAY_SPEC)
                return w

@android.register_module_callback
def _(android): android.home = Home(android)
