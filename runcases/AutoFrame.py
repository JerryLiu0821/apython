#Boa:Frame:BoaTest
# -*- coding: utf-8 -*-

import wx
import wx.richtext
import wx.lib.scrolledpanel
import os,sys,commands,time

from CaseHandler import *
from Utils import *


def create(parent):
    return BoaTest(parent)

[wxID_BOATEST,wxID_BOATESTBTN_RECORD, wxID_BOATESTBTN_REPLAY, wxID_BOATESTBTN_START, wxID_BOATESTBTN_STOP, 
 wxID_BOATESTCHECKLISTBOX1, wxID_BOATESTLOG, wxID_BOATESTID, 
 wxID_BOATESTLIST, wxID_BOATESTLOOP, 
 wxID_BOATESTSTATICTEXT1, wxID_BOATESTSTATICTEXT2, wxID_BOATESTSTATICTEXT3, 
 wxID_BOATESTSTATICTEXT4, 
] = [wx.NewId() for _init_ctrls in range(14)]

class BoaTest(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_BOATEST, name=u'BoaTest', parent=prnt,
              pos=wx.Point(460, 258), size=wx.Size(800, 600),
              style=wx.DEFAULT_FRAME_STYLE, title=u'BoaTest')
        self.SetClientSize(wx.Size(800, 600))

        self.staticText1 = wx.StaticText(id=wxID_BOATESTSTATICTEXT1,
              label=u'id', name='staticText1', parent=self, pos=wx.Point(30,
              40), size=wx.Size(70, 20), style=0)

        self.id = wx.ComboBox(choices=self.GetConnectDevice(), id=wxID_BOATESTID, name=u'id',
              parent=self, pos=wx.Point(100, 30), size=wx.Size(250, 30),
              style=0, value=u'default value')

        self.staticText2 = wx.StaticText(id=wxID_BOATESTSTATICTEXT2,
              label=u'case', name='staticText2', parent=self, pos=wx.Point(30,
              80), size=wx.Size(70, 20), style=0)

        self.list = wx.Choice(choices=self.GetDirFileOrDir(self.testcase_dir, 'f'), id=wxID_BOATESTLIST, name=u'list',
              parent=self, pos=wx.Point(100, 70), size=wx.Size(250, 30),
              style=0)
        self.list.Bind(wx.EVT_CHOICE, self.OnListChoice, id=wxID_BOATESTLIST)

        self.staticText3 = wx.StaticText(id=wxID_BOATESTSTATICTEXT3,
              label=u'loops', name='staticText3', parent=self, pos=wx.Point(30,
              120), size=wx.Size(70, 20), style=0)

        self.loop = wx.SpinCtrl(id=wxID_BOATESTLOOP, initial=1, max=99999,
              min=1, name=u'loop', parent=self, pos=wx.Point(100, 110),
              size=wx.Size(250, 30), style=wx.SP_ARROW_KEYS)

        self.staticText4 = wx.StaticText(id=wxID_BOATESTSTATICTEXT3,
              label=u'log dir', name='staticText4', parent=self,
              pos=wx.Point(30, 160), size=wx.Size(70, 20), style=0)

        self.log = wx.ComboBox(choices=self.GetDirFileOrDir('../', 'd'), id=wxID_BOATESTLOG, name=u'log_directory',
              parent=self, pos=wx.Point(100,150), size=wx.Size(250, 30),
              style=0, value=u'')

        self.btn_start = wx.Button(id=wxID_BOATESTBTN_START, label=u'START',
              name=u'btn_start', parent=self, pos=wx.Point(50, 280),
              size=wx.Size(80, 30), style=0)
        self.btn_start.Bind(wx.EVT_BUTTON, self.OnBtn_startButton,
              id=wxID_BOATESTBTN_START)

        self.btn_stop = wx.Button(id=wxID_BOATESTBTN_STOP, label=u'STOP',
              name=u'btn_stop', parent=self, pos=wx.Point(180, 280),
              size=wx.Size(80, 30), style=0)
        self.btn_stop.Bind(wx.EVT_BUTTON, self.OnBtn_stopButton,
              id=wxID_BOATESTBTN_STOP)

        self.checkListBox1 = wx.CheckListBox(choices=[],
              id=wxID_BOATESTCHECKLISTBOX1, name='checkListBox1', parent=self,
              pos=wx.Point(360, 32), size=wx.Size(424, 152), style=0)
        self.checkListBox1.Bind(wx.EVT_CHECKLISTBOX,
              self.OnCheckListBox1Checklistbox, id=wxID_BOATESTCHECKLISTBOX1)

        self.btn_record = wx.Button(id=wxID_BOATESTBTN_RECORD, label=u'record',
              name=u'btn_record', parent=self, pos=wx.Point(50, 540),
              size=wx.Size(80, 30), style=0)
        self.btn_record.Bind(wx.EVT_BUTTON, self.OnBtn_recordButton,
              id=wxID_BOATESTBTN_RECORD)

        self.btn_replay = wx.Button(id=wxID_BOATESTBTN_REPLAY, label=u'replay',
              name=u'btn_replay', parent=self, pos=wx.Point(180, 540),
              size=wx.Size(80, 30), style=0)
        self.btn_replay.Bind(wx.EVT_BUTTON, self.OnBtn_replayButton,
              id=wxID_BOATESTBTN_REPLAY)

    def __init__(self, parent):
        self.testcase_dir = u'../testcases'
        self.list_dir = u'./List'
        self.parent = parent
        self._init_ctrls(parent)
        self.classList = ''
        self.caseList = []
        self.methonsList = []


    def GetId(self):return self.id.GetValue()
    
    def GetMethons(self): return self.GetDirFileOrDir(self.testcase_dir,'f')[self.list.GetCurrentSelection()]
    
    def GetLoop(self): return self.loop.GetValue()

    def GetLogDir(self): return self.log.GetValue()
    
    def GetConnectDevice(self):
        '''
        parm: None
        return: list of devices connected on pc
        '''
        device = []
        status, output = commands.getstatusoutput(u'adb devices')
        if not status:
            output=output.split(os.linesep)
            output.pop()
            output.remove(output[0])
            print output
            for d in output:
                device.append(d.split('\t')[0])
        return device
    
    def GetDirFileOrDir(self, dir, type):
        '''
        parm: a directory
        return: a file list or dir list
        '''
        f = []
        for file in os.listdir(dir):
            file = os.path.join(dir,file)
            if type == 'f':
                if os.path.isfile(file) and os.path.splitext(file)[1]!='.pyc':
                    f.append(file)
            elif type == 'd':
                if os.path.isdir(file):
                    f.append(file)

        return f
    
    def validate(self):
        id = self.GetId()
        lname = self.GetMethons()
        times = self.GetLoop()
        if id not in self.GetConnectDevice():
            return False
        else:
            fp = open('TV_temp.py', 'w+')
            try:
                fp.write('DEVICES={')
                fp.write('\'TestDevice\':{\'id\':\'%s\'},' %id)
                fp.write('}')
                fp.close()
            except Exception:
                print Exception
                fp.close()
                return False
            finally:
                fp.close()
        return True
    
    def OnBtn_startButton(self, event):
        if not self.validate():
            wx.MessageBox('Please Check Condition', 'ERROR', wx.OK)
            return self
        for i in range(self.GetLoop()):
            if self.methonsList != []:
                for each in self.methonsList:
                    print type(self.GetMethons()), type(self.classList),type(each)
                    self.caseList.append(self.GetMethons()+':'+self.classList+'.'+each)
            else:
                self.caseList.append(self.GetMethons())
        writeFile(self.caseList, os.path.join('./List','list_tmp'))
        self.rc = run_case(self.GetId(), 'list_tmp', self.GetLogDir())
        self.rc.setDaemon(True)
        self.rc.start()
        self.btn_start.Disable()
        

    def OnBtn_stopButton(self, event):
        closed = self.rc.killRunningScript()
        self.btn_start.Enable()


    def OnListChoice(self, event):
        print 'choose %s' %self.GetMethons()
        case_include_class = GetScriptCases(self.GetMethons())
        self.classList = case_include_class[0]
        self.checkListBox1.SetItems(case_include_class[1:])
        event.Skip()

    def OnCheckListBox1Checklistbox(self, event):
        self.methonsList= self.checkListBox1.GetCheckedStrings()
        """
        #this method will choose many testcase and methons
        for each in cl:
                    self.caseList.append(self.GetMethons()+":"+self.case_include_class[0]+'.'+each)"""
        event.Skip()

    def OnBtn_recordButton(self, event):
        if self.GetId() not in self.GetConnectDevice():
            wx.MessageBox('Please Choose a Device for Test!!', 'ERROR', wx.OK)
            return self
        rr = RecordReplay(self.GetId())
        def onStatus(args):
            if args == 'record':
                rr.record()
                self.btn_record.SetLabel('stop')
            elif args  == 'stop':
                rr.stopRecord()
                self.btn_record.SetLabel('record')
        stu = self.btn_record.GetLabelText()
        onStatus(stu)

        event.Skip()

    def OnBtn_replayButton(self, event):
        rr = RecordReplay(self.GetId())
        def onStatus(args):
            if args == 'replay':
                rr.replay()
                self.btn_replay.SetLabel('stop')
            elif args == 'stop':
                rr.stopReplay()
                self.btn_replay.SetLabel('replay')
        status = self.btn_replay.GetLabelText()        
        onStatus(status)
        event.Skip()


