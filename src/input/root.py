# -*- coding: utf-8 -*-

import wx

from shs.sio import FDFFile
from shs.options import Options
from shs.geom import Geom

from control import ControlPN
from system import SystemPN
from electrons import ElectronsPN
from ions import IonsPN
from extra import ExtraPN
import fdf_base as fdf

class RootFrame(wx.Frame):
    
    def __init__(self, *args, **kwds):
        
        wx.Frame.__init__(self, *args, **kwds)
        self.fdfmenu = self.CreateMenuBar()
        self.SetMenuBar(self.fdfmenu)

        self.NB = wx.Notebook(self, -1, style = 0)
        Control = ControlPN(self.NB, -1)
        System = SystemPN(self.NB, -1)
        Electrons = ElectronsPN(self.NB, -1)
        Ions = IonsPN(self.NB, -1)
        Extra = ExtraPN(self.NB, -1)
        
        self.pages = [Control,
                      System,
                      Electrons,
                      Ions,
                      Extra]
        self.names = ['Control',
                      'System',
                      'Electrons',
                      'Ions',
                      'Extra']
        
        self.ImportBtn = wx.Button(self, -1, 'Import...')
        self.ExportBtn = wx.Button(self, -1, 'Export...') 
        self.BatchBtn = wx.Button(self, -1, 'Batch')
        
        # binding events to buttons
        self.Bind(wx.EVT_BUTTON, self.OnImport, self.ImportBtn)
        self.Bind(fdf.EVT_COMBOSIZER, Ions.OnCT, Control.CalcType)
        
        self.__set_properties()
        self.__do_layout()    



    def OnImport(self, evt):
        'Gets FDF file dictionary'
        dlg = wx.FileDialog(self, 'Choose FDF file to import', wildcard = '*.fdf', style = wx.ID_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            fdfn = dlg.GetPath()
            fdff = FDFFile(fdfn)
            # get options 
            fdfo = Options(fdff.d)
            self.ImportFDF(fdfo.opts)
        dlg.Destroy()
        
    def ImportFDF(self, d):
        'Imports FDF dictionary to shs-init'
        for page in self.pages:
            # taking all controls from the page 
            ctrls = {}
            for key in page.fdf_opts.keys():
                ctrls.update(page.fdf_opts[key])
            for option, value in d.items():
                if option in ctrls.keys():
                    ctrls[option].SetValue(value)
                    d.pop(option)
        # all remaining options go to extras
        self.pages[-1].Populate(d)
                    
    
    def __set_properties(self):
        pass

    def __do_layout(self):
        for page, name in zip(self.pages, self.names):
            self.NB.AddPage(page, name)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.NB, 2, wx.ALL | wx.EXPAND, 5)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.ImportBtn, 0, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.ExportBtn, 0, wx.ALL | wx.EXPAND, 5)
        btn_sizer.Add(self.BatchBtn, 0, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Center()


    def CreateMenuBar(self):
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(wx.NewId(), 'New...', '', wx.ITEM_NORMAL)
        menu.Append(wx.NewId(), 'Exit', '', wx.ITEM_NORMAL)
        menubar.Append(menu, 'File')
        menu = wx.Menu()
        menu.Append(wx.NewId(), 'About', '', wx.ITEM_NORMAL)
        menubar.Append(menu, 'Help')
        return menubar
        
        