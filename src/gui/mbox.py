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

def JobSubmit(q, comm):
    if q is None:
        wx.MessageBox('Haven\'t found any queue system', 'Failure', 
                  wx.OK | wx.ICON_ERROR)
        return None
    else:
        q_str = 'Used batch system: %s\n' % (q,)
    wx.MessageBox(q_str + comm[0], 'Success', 
                  wx.OK | wx.ICON_INFORMATION)
    if comm[1] != '':
        wx.MessageBox(comm[1], 'Errors during submit', 
                  wx.OK | wx.ICON_ERROR)



def ShowPlotInfo(leg, info):
    s = ''
    for it, t in enumerate(leg):
        s += '%s\n' % (t,)
        for i in info[it].keys():
            s += '%s     %10s\n' % (i, str(info[it][i]))
        s += '\n'
    wx.MessageBox(s, 'Plot information', 
                  wx.OK | wx.ICON_INFORMATION)
        