import android, unittest, time, sys, traceback

import subprocess



class testSetup(unittest.TestCase):
    """setup """

    def setUp(self):
        try :
            self.a = android.connect()

        except :
            self.a.log.debug("", "\n Set up")

    def tearDown(self):
        pass
            
    def testSetLanguage(self):
        """ testSetLanguage | set language to English"""
        try:
            if self.runShellCmd('sh testcases/setup/SetLanguage.sh'):
                time.sleep(2)
                pass
            else:
                raise Exception

        except:
            self.a.log.debug("", "\n testSetLanguage")
            self.fail(self.error)
            
            
    def runShellCmd(self, cmd):
        try:
            process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            (stdout, stderr) = process.communicate()
            print stdout
            print stderr
            return True
        except Exception, e:
            print e
            return False

if __name__ == '__main__':
    unittest.main()


