import android, unittest, time, sys, traceback

import subprocess
import Stability


class testSetup(unittest.TestCase):
    """setup """

    def setUp(self):
        try :
            self.setup = Stability.SetupDeviceConnections()
            self.a = self.setup.initializeTestDevice()
            self.id= self.setup.device_id
            self.stabdl=Stability.StabDL(self.a)

        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass
            
    def testInstallESFileExplore(self):
        """ testInstallESFileExplore | Install ESFileExplore to device"""
        try:
            if 'Success' in self.runShellCmd('adb -s %s install -r ../testcases/setup/ESFileExplorer.apk'%(self.id)):
                pass

            else:
                raise Exception

        except:
            self.a.log.debug("", "\n testInstallESFileExplore")
            self.fail(self.error)
            
            
    def runShellCmd(self, cmd):
        try:
            process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            (stdout, stderr) = process.communicate()
            print stdout
            print stderr
            return stdout
        except Exception, e:
            print e
            return False

if __name__ == '__main__':
    unittest.main()


