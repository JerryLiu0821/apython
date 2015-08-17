import android, unittest, time, sys, traceback
import inspect
from random import choice
sys.path.append('../testcases')
import runtests
import Stability



class testStressapptest(unittest.TestCase):
    """Stress app test """

    def setUp(self):
        try :
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id= self.setup.device_id

        except Exception, e :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass
            
    def testSTAB_STRESS_APP_TEST(self):
        """内存压力测试 | stressapptest"""
        try:
            filename = 'stressapptest_%s_log.txt'%(self.id)
            abs_path = os.path.join(android.log.report_directory(), android.log.logs_directory(), filename)
            cmd ='adb -s %s shell stressapptest -s 28800 -M 400 -m 8 -i 8 -v 13 > %s'%(self.id, abs_path)
            os.system (cmd)
            if  not self.readfiles(abs_path):
                raise Exception      
                                             
        except Exception, e :
            self.a.log.debug("", "\n testSTAB_LETV_PLAY")
            self.fail("Failed, please check the log file %s"% (abs_path))
    
    def pushStressapptest(self):
        os.system('adb -s %s remount')
        time.sleep(1)
        os.system('adb -s %s push ../testcases/setup/stressapptest /system/bin/' %self.id)
        os.system('adb -s %s shell chmod 777 /system/bin/stressapptest' %self.id)
        

    def readfiles(self, filename):
        try:            
            file = open(filename)
            lastLine = mLine = ""
            while 1:
                if mLine != '\r\n':
                    lastLine=mLine
                mLine = file.readline()
                if not mLine :
                    break;

            if 'PASS' in lastLine:
                return True
            else:
                return False
                    
        except:
            return False
        finally:
            file.close()

    

if __name__ == '__main__':
    unittest.main()


