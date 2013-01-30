#!/usr/bin/env python

import wx

oneline = 'A module which contains various messageboxes for SHS GUI'

def WrongInput():  
    wx.MessageBox('PLease enter positive or negative numbers divided by space', 'Warning', 
                  wx.OK | wx.ICON_WARNING)
    
def NoResults(cdir, ctype):
    wx.MessageBox(cdir + ' doesn\'t contain SIESTA results of type ' + ctype, 'Warning', 
                  wx.OK | wx.ICON_WARNING)

def NoInfo():
    wx.MessageBox('Calculations provided no information', 'Warning', 
                  wx.OK | wx.ICON_WARNING)


def DataExported(ddir):
    wx.MessageBox('Data successfully exported to ' + ddir, 'Export successful', 
                  wx.OK | wx.ICON_INFORMATION)

def ShowPlotInfo(leg, info):
    s = ''
    for it, t in enumerate(leg):
        s += '%s\n' % (t,)
        for i in info[it].keys():
            s += '%s     %10s\n' % (i, str(info[it][i]))
        s += '\n'
    wx.MessageBox(s, 'Plot information', 
                  wx.OK | wx.ICON_INFORMATION)
        