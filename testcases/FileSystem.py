# -*- coding: utf-8 -*-
'''
Created on Jul 10, 2013

@author: liujian

Modified on 2013-11-25 by ZhaoJIanning, add case of creating dir
'''
import unittest
import Stability,android
import time, subprocess
import os

class TestFileSystem(unittest.TestCase):
    """This will include some file system cases"""

    def setUp(self):
        self.error=""
        self.path="/mnt/usb/sda1"
        self.path2="/mnt/usb/sda2"
        self.setup = Stability.SetupDeviceConnections()
        self.a = self.setup.initializeTestDevice()
        self.id = self.setup.device_id
        self.a.input.back(3)
        
        self.longEnfile="1234" * 63
        self.longChfile="你好乐视" * 63 #255characters
        
        self.filename="filesystem.test"
        self.dir = "dir"
        self.subDir = "subdir" 
        self.dirFile = "dir"
        self.subDirFile = "subdir"
        self.multipleDir = "root/sub1/sub2/sub3/sub4/sub5/sub6/sub7/sub8/sub9/sub10/sub11/sub12/sbu13/sub14/sub15/sub16/sub17/sub18/sub19/"


    def tearDown(self):
        self.a.device.sh("rm %s/%s" %(self.path, self.longChfile))
        self.a.device.sh("rm %s/%s" %(self.path, self.longEnfile))
        
    def checkScreen(self, screen):
        try:
            self.a.input.back()
            if screen in self.a.ui.window():
                return True
            else:
                return False
        except:
            return False
    
    def testFileState(self):
        """文件属性显示|操作步骤:;1. stat /mnt/usb/sda1/filesystem.test;Fail项:;1. \"IO Block\"在结果中显示"""
        try:
            self.isFileExistByName(self.path, self.filename)
            self.a.device.sh("touch %s/%s" %(self.path, self.filename))
            state = self.a.device.sh("busybox stat %s/%s" %(self.path, self.filename))
            if "IO Block" not in state:
                self.error="stat %s/%s Failed: %s" %(self.path, self.filename, state)
                raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testFileState")
            self.fail("Error happened: %s %s" % (self.error, e))
        
        
    
    def testLongFileName(self):
        """长文件名 |操作步骤:;1. 创建255字符的英文文件;2. 创建255字符的中文文件;Fail项:;1. 只要有一个不能创建成功"""
        try:
            self.isFileExistByName(self.path, self.longEnfile)
            self.isFileExistByName(self.path, self.longEnfile)
            resultCh = self.a.device.sh("touch %s/%s" %(self.path, self.longChfile))
            resultEn = self.a.device.sh("touch %s/%s" %(self.path, self.longEnfile))
            if resultCh == None and resultEn == None:
                pass
                
            else:
                self.error += resultEn
                self.error += resultCh
                raise Exception
                
            
        except Exception, e:
            self.a.log.debug("", "\n testLongFileName")
            #self.fail("Error happened: %s %s" % (self.error, e))
            
    def testCopyFiletoDevice(self):
        """文件复制|操作步骤：;1. busybox dd if=/dev/zero of=/mnt/usb/sda1/file.tmp bs=1M count=512;Fail项：;1. 写入的文件不是512M"""
        try:
            cmd = "busybox dd if=/dev/zero of=%s/file.tmp bs=1M count=512" %self.path
            self.isFileExistByName(self.path,"file.tmp")
            result = self.a.device.sh(cmd)
            if "536870912 bytes (512.0MB) copied" not in result:
                self.error=result
                print self.error
                raise Exception
            filecmd = "busybox du -sh %s/file.tmp" %self.path
            filesize = self.a.device.sh(filecmd)
            if "512.0M" not in filesize:
                self.error="cannot copy 512M file: %s" %filesize
                print self.error
                raise Exception
            md5sum = self.a.device.sh("busybox md5sum %s/file.tmp" %self.path).encode("utf-8").strip().split(" ")[0]
            print md5sum
            if (md5sum != "aa559b4e3523a6c931f08f4df52d58f2"):
                self.error = "the md5sum isn't correct"
                raise Exception
            
        except Exception, e:
            self.a.log.debug("", "\n testCopyFiletoDevice")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testCreateDir(self):
        """创建2级目录|操作步骤：；1.mkdir /mnt/usb/sda1/dir/subdir 2. dir目录下创建文件dir dir/subdir/目录下创建文件subdir；"""
        try:
            cmd1 = "mkdir %s/%s" %(self.path, self.dir)
            cmd2 = "mkdir %s/%s/%s" %(self.path, self.dir, self.subDir)
            cmd3 = "echo \"it is root dir file\" > %s/%s/%s" %(self.path, self.dir, self.dirFile)
            cmd4 = "echo \"it is sub dir file\" > %s/%s/%s/%s" %(self.path, self.dir, self.subDir, self.subDirFile)
            if not "No such file or directory" in self.a.device.sh("ls %s/%s" %(self.path, self.dir)):
                print "remove the existed dir"
                self.a.device.sh("rm -rf %s/%s" %(self.path, self.dir))
            output1 = self.a.device.sh(cmd1)
            if output1 == '':
                output2 = self.a.device.sh(cmd2)
                output3 = self.a.device.sh(cmd3)
                if output2 != '':
                    self.error = "failed to create subdir"
                    raise Exception
                else:
                    output4 = self.a.device.sh(cmd4)
                    if output4 != '':
                        self.error = "failed to create the subdir file"
                        raise Exception
                    else:
                        subdir_sum = self.a.device.sh("busybox md5sum %s/%s/%s/%s" %(self.path, self.dir, self.subDir, self.subDirFile)).encode("utf-8").strip().split(" ")[0]
                        if subdir_sum != "42fa960aafbdfb056b28963a4e1cb2d9":
                            print subdir_sum
                            self.error = "the md5sum of subdir file isnot correct"
                            raise Exception
                if output3 != '':
                    self.error = "failed to create the dir file"
                    raise Exception
                else:
                    dir_sum = self.a.device.sh("busybox md5sum %s/%s/%s" %(self.path, self.dir, self.dirFile)).encode("utf-8").strip().split(" ")[0]
                    if dir_sum != "24b2095cfdfa459df942cf72b199adf2":
                        print dir_sum
                        self.error = "the md5sum of dir file isnot correct"
                        raise Exception
            else:
                self.error = "failed to create dir folder"
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testCreateDir")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testMultipleSubDir(self):
        """播放外接存储器的20层文件夹的音乐文件|操作步骤：；1.检查外接存储器内的文件是否能被检测出 2. 能否正常播放；Fail项：；1.无法找到该音乐文件，2.文件播放不成功"""
        try:
            cmd = "df | busybox awk -F ' ' '/\/mnt\/usb\/sd[a-z][0-9]*/{print $1}'"
            storagePath = self.a.device.sh(cmd).encode("utf-8").strip().split('\r\n')
            if storagePath != '':
                for i in range(len(storagePath)):
                    cmd2 = "ls %s/%s" %(storagePath[i], self.multipleDir)
                    result = self.a.device.sh(cmd2)
                    print result
                    if 'xuanmu.mp3' in result:
                        print 'find the mp3'
                        mediaPath = "%s/%s" %(storagePath[i], self.multipleDir)
                        print mediaPath
                        break
                    elif i == len(storagePath):
                        print i
                        self.error = "can't find the storage which contains media folder"
                        raise Exception
            cmd3 = "am start -a android.intent.action.VIEW -n com.letv.videoplayer/.MainActivity -d file://%sxuanmu.mp3" %mediaPath
            print self.a.device.sh(cmd3)
            time.sleep(15)
            if "player_error_info_tv" in self.a.ui.screen().ids():
                print "can"
                self.error = "cannot play file"
                raise Exception
            self.a.input.center()
            time.sleep(2)
            if 'xuanmu.mp3' not in self.a.ui.screen().texts()[0]:
                self.error = "play failed"
                raise Exception
            else:
                self.a.input.back()
        except Exception, e:
            self.a.log.debug("", "\n testCreateMultipleSubDir")
            self.fail("Error happened: %s %s" % (self.error, e))
            
    def testMountPoint(self):
        '''检测挂载点是否正确|检测挂载点是否正确'''
        try:
            cmd = "df | busybox awk -F ' ' '/\/mnt\/usb\/sd[a-z][0-9]*/{print $1}'"
            os.system ('adb -s %s root'%self.id)
            time.sleep(2)
            os.system ('adb connect '+ self.id )
            storagePath = self.a.device.sh(cmd).encode("utf-8").strip().split('\r\n')
            print storagePath
            if storagePath == '':
                self.error = 'the mount point is not correct or not connect the device'
                raise Exception
        except Exception, e:
            self.a.log.debug("", "\n testMountPoint")
            self.fail("Error happened: %s %s" % (self.error, e))
                        
    
    def isFileExistByName(self,path,filename):
        cmd = "ls %s" %path
        if filename  in self.a.device.sh(cmd):
            self.a.device.sh("rm %s/%s" %(path,filename))
            
    def runShell(self, cmd):
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            stdout = p.communicate()[0]
            return stdout
        except:
            return ''
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
