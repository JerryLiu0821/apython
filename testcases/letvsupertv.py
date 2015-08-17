# -*- coding: utf-8 -*-
#上面的一行添加以后可以在脚本中使用中文
'''
Created on 2014-09-12

@author: gaojianhua
'''
import unittest
import Stability
import time

#上面用来添加需要引入的模块

class testopenplayletvsupertv(unittest.TestCase):
    
        
         
    def setUp(self):#这里做一些初始操作，连接设备，必须在这里
        self.error = ''
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.a.input.back(3)


    def tearDown(self):#这里做善后操作，脚本执行完成了以后执行
        #self.a.input.back(3)
        pass
        
    def launchTVban(self):
        self.a.device.sh("am start -a android.intent.action.MAIN -n com.letv.tv/.activity.MainActivity")
        time.sleep(10)
        if "com.letv.tv/com.letv.tv.activity.MainActivity" not in self.a.ui.window():
            print 'cannot go to tv ban'
            raise Exception

  
    def testplaygujianqitanseconds(self):
        """反复播放退出点播视频|反复播放退出点播视频"""
        self.launchTVban()
        time.sleep(5)    
        self.a.input.center()
        time.sleep(8)    
        self.a.input.center()
        time.sleep(8)
        self.a.input.back(2)
       
        
if __name__ == "__main__":
    #主程序，程序的入口
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()