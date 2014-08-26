import wx


class FillInNBPage(wx.ScrolledWindow):

    def __init__(self, *args, **kwds):
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self.__set_properties()
        self.__do_layout()

    def add_option(self, option):
        self.sizer.Add(option.sizer, 0, wx.EXPAND|wx.ALL, 2)
        self.Layout()

    def remove_option(self):
        idx = len(self.sizer.GetChildren())-1
        self.sizer.Hide(idx)
        self.sizer.Remove(idx)
        self.Layout()

    def __len__(self):
        return len(self.sizer.GetChildren())

    def __set_properties(self):
        pass

    def __do_layout(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.Layout()
