#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import AutoFrame

modules ={'AutoFrame': [1, 'Main frame of Application', u'AutoFrame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = AutoFrame.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

def main():
    
    application = BoaApp(False) 
    #True to open redrect
    application.MainLoop()

if __name__ == '__main__':
    main()
