import wx

class AddBlockDlg(wx.Dialog):
    
    def __init__(self, *args, **kwds):
        if 'def_opt' in kwds.keys():            
            def_opt = kwds.pop('def_opt')
        else:
            def_opt = ''
        if 'def_val' in kwds.keys():            
            def_val = kwds.pop('def_val')
        else:
            def_val = ''

        wx.Dialog.__init__(self, *args, **kwds)
        self.OptL = wx.StaticText(self, -1, 'Option')
        self.ValL = wx.StaticText(self, -1, 'Value')
        self.OptTE = wx.TextCtrl(self, -1, def_opt)
        self.ValTE = wx.TextCtrl(self, -1, def_val, style = wx.TE_MULTILINE)
        self.__set_properties()
        self.__do_layout()
        
    def GetBlock(self):
        'Returns option and block value'
        return self.OptTE.GetValue(), self.ValTE.GetValue() 
        
    def __set_properties(self):
        self.SetTitle("Add block to extra options")

    def __do_layout(self):
        opt_sizer = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=15)
        opt_sizer.Add(self.OptL, 0, wx.ALL, 0)
        opt_sizer.Add(self.OptTE, 0, wx.ALL|wx.EXPAND, 0)
        opt_sizer.Add(self.ValL, 0, wx.ALL, 0)
        opt_sizer.Add(self.ValTE, 0, wx.ALL|wx.EXPAND, 0)
        opt_sizer.AddGrowableRow(1, 1)
        opt_sizer.AddGrowableCol(1, 1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(opt_sizer, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.CreateSeparatedButtonSizer(wx.OK|wx.CANCEL), 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Layout()
