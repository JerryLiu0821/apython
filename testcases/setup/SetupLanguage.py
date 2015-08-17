import android, unittest, time, sys, traceback
import Stability
import subprocess

from random import choice

import runtests


class testLivePlay(unittest.TestCase):
    """Live_Play """

    def setUp(self):
        try :
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id= self.setup.device_id
            self.stabdl=Stability.StabDL(self.a)
            #self.a.input.down()
            #self.a.input.center()
            self.a.input.back(2)       


        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass         
            
    def test_SETLANGUAGE(self):
        """ test_SETLANGUAGE | set up language to English """
        try :              
            self.a.device.sh('am start -n com.android.settings/.inputmethod.InputMethodAndLanguageSettingsActivity')
            self.a.input.center()
            self.a.input.down(2)
            self.a.input.center()
            self.a.input.back(3)
                    
            
                        
        except Exception, e :
            self.a.log.debug("", "\n test_SETLANGUAGE")
            self.fail("")


                
          

if __name__ == '__main__':
    unittest.main()


