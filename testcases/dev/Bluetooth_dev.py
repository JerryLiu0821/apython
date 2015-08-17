import android, unittest, time, sys, traceback
sys.path.append('../testcases')
import Stability
import inspect
import re
import runtests

from random import choice


class testBluetooth(unittest.TestCase):
    """Bluetooth connect and disconnect """
    
    def setUp(self):
        try :
            self.loop = 30
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            #self.stabdl=Stability.StabDL(self.a)   
            self.a.input.back(3)

        except Exception, e:
            self.a.log.debug("", "\n Set up")
            
     
    def tearDown(self):
        try :
            self.a.input.back(3)
            #time.sleep(3)
        except :
            self.a.log.debug("", "\n Tear down")


    def launchBT(self):
        print "finding bluetooth"
        self.a.device.sh("input keyevent 176")
        time.sleep(3)
        self.a.input.up()
        time.sleep(3)
        self.a.input.left(10)
        time.sleep(3)
        '''
        self.a.input.right(4)
        time.sleep(3)
        self.a.input.center()
        time.sleep(5)
        print "down key"
        self.a.input.down(3)
        self.a.input.center()
        '''
        settingScreen = self.a.ui.screen().texts()
        print settingScreen
        if '\u914d\u4ef6\u8bbe\u7f6e' in str(settingScreen):
            print 'find bluetooth in current screen'
            for i in range(0,8):
                if '\u914d\u4ef6\u8bbe\u7f6e' in str(settingScreen[i]):
                    if i == 0:
                        print 'curren icon is bluetooth'
                        self.a.input.center()
                        time.sleep(3)
                        self.a.input.down()
                        time.sleep(3)
                        self.a.input.center()
                        return True
                    elif 0 < i < 4:
                        self.a.input.right(i)
                    elif 3 < i < 8:
                        self.a.input.down()
                        time.sleep(3)
                        self.a.input.right(i-4)
        else:
            self.a.input.right(4)
            time.sleep(3)
            settingScreen = self.a.ui.screen().texts()
            if '\u914d\u4ef6\u8bbe\u7f6e' not in str(settingScreen):
                return False
            else: 
                for i in range(0,8):
                    if '\u914d\u4ef6\u8bbe\u7f6e' in str(settingScreen[i]):
                        if i == 0:
                            print 'curren icon is bluetooth'
                            self.a.input.center()
                            time.sleep(3)
                            self.a.input.down()
                            time.sleep(3)
                            self.a.input.center()
                            return True
                        elif 0 < i < 4:
                            self.a.input.right(i)
                        elif 3 < i < 8:
                            self.a.input.down()
                            time.sleep(3)
                            self.a.input.right(i-4)
        self.a.input.center()
        time.sleep(3)
        self.a.input.down()
        time.sleep(3)
        self.a.input.center()
        return True
        
        
    def turnOnBT(self):
        #self.a.input.up()
        if 'search_equipment' in self.a.ui.screen().ids():
            self.a.input.center()
            time.sleep(5)
        self.a.input.center()
        time.sleep(5)
        if 'search_equipment' in self.a.ui.screen().ids():
            print "open bluetooth successfully"
        else:
            if 'Application Error' in str(self.a.ui.windows()):
                self.error = 'meets crash'
            else:
                self.error = 'failed to open bluetooth'
            return False
        self.a.input.center()
        if 'search_equipment' not in self.a.ui.screen().ids():
            print "off bluetooth successfully"
            time.sleep(10)
        else:
            if 'Application Error' in str(self.a.ui.windows()):
                self.error = 'meets crash'
            else:
                self.error = "failed to close bluetooth"
            return False
        return True
         
    def testSTAB_connect_disconnect(self):
        """Bluetooth test| connect and disconnect bluetooth """
        try :
            '''if not self.launchBT():
                runtests.log_screenshot(self.a, '', 'screenshot', 'bluetooth_01')
                self.error = 'failed to find bluetooth'
                raise Exception'''
            self.a.device.sh('input keyevent 176')
            time.sleep(2)
            self.a.input.up()
            self.a.input.left(8)
            self.a.input.right(3)
            self.a.input.down()
            self.a.input.center()
            time.sleep(2)
            self.a.input.up(2)
            self.a.input.down()
            self.a.input.center()
            time.sleep(2)
            for i in range(0, self.loop):
                if not self.turnOnBT():
                    runtests.log_screenshot(self.a, '', 'screenshot', 'bluetooth_02')
                    print "failed at %s" %i
                    raise Exception
           
        except Exception, e :
            self.a.log.debug("", "\n bluetooth")
            self.fail("Error happened: %s" % (self.error))
      

            
   


if __name__ == '__main__':
    unittest.main()


