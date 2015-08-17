# -*- coding: utf-8 -*-
#上面的一行添加以后可以在脚本中使用中文
'''
Created on 2013-10-9

@author: Administrator
'''
import unittest
import Stability
import time

#上面用来添加需要引入的模块

class TestLauncher(unittest.TestCase):


    def setUp(self):#这里做一些初始操作，连接设备，必须在这里
        self.error = ''
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.a.input.back(3)


    def tearDown(self):#这里做善后操作，脚本执行完成了以后执行
        self.a.input.back(3)


    def testreboot_test(self):#真正的测试从这里开始
        """通过节目菜单列表做轮播台切换|通过节目菜单列表做轮播台切换."""
        #上面的是注释部分，必须用上面的格式来书写，测试报过会反应出来
        try:
                
            self.a.input.center()
            #调出播放列表
            time.sleep(3)
            self.a.input.up(1)
            #向上一下   
            time.sleep(5)
            self.a.input.center()
            #换台
            time.sleep(5)
            self.a.input.center()
            #调出播放列表 
            time.sleep(2)
            self.a.input.down(3)
            #向下三下      
            time.sleep(5)
            self.a.input.center()
            #换台
            time.sleep(5)
            self.a.input.center()
            #调出播放列表
            time.sleep(2)
            self.a.input.up(1)
            #向上一下      
            time.sleep(2)
            self.a.input.center()
            #换台
            time.sleep(5)
        except Exception,e:#异常和case失败以后会跳到这里执行
            self.a.log.debug("", "\n testName")
            self.fail("Error happened: %s %s" % (self.error, e))


if __name__ == "__main__":
    #主程序，程序的入口
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
