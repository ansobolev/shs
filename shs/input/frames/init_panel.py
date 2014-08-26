import wx

from ..fdf_optionlist import FDFOptionList


class NBPage(wx.ScrolledWindow):

    def __init__(self, *args, **kwds):
        panel = kwds.pop("panel")
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        self.ol = FDFOptionList(self, panel)
        self.__set_properties()
        self.__do_layout()
    
    def __set_properties(self):
        self.SetScrollRate(0, 10)

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        box = ""
        box_proportion = 0
        for option in self.ol:
            if not box and not option.box:
                main_sizer.Add(option.sizer, option.proportion, wx.ALL | wx.EXPAND, 2)
            elif not box and option.box:
                box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, option.box), wx.VERTICAL)
                box = option.box
                box_sizer.Add(option.sizer, option.proportion, wx.ALL | wx.EXPAND, 2)
                if option.proportion > box_proportion:
                    box_proportion = option.proportion
            elif box and option.box:
                if box == option.box:
                    box_sizer.Add(option.sizer, option.proportion, wx.ALL | wx.EXPAND, 2)
                    if option.proportion > box_proportion:
                        box_proportion = option.proportion
                else:
                    main_sizer.Add(box_sizer, box_proportion, wx.ALL | wx.EXPAND, 2)
                    box_proportion = 0
                    box_sizer = wx.StaticBoxSizer(wx.StaticBox(self, -1, option.box), wx.VERTICAL)
                    box = option.box
                    box_sizer.Add(option.sizer, option.proportion, wx.ALL | wx.EXPAND, 2)
                    if option.proportion > box_proportion:
                        box_proportion = option.proportion
            elif box and not option.box:
                box = ""
                main_sizer.Add(box_sizer, box_proportion, wx.ALL | wx.EXPAND, 2)
                main_sizer.Add(option.sizer, option.proportion, wx.ALL | wx.EXPAND, 2)
                box_proportion = 0
            # hide initially hidden options
            if option.hidden:
                option.Show(False)
        # add the last box to the main sizer
        if box:
            main_sizer.Add(box_sizer, box_proportion, wx.ALL | wx.EXPAND, 2)

        self.SetSizer(main_sizer)
        self.Fit()
