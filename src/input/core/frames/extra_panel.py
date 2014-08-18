#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import wx

from ..dialogs.add_block import AddBlockDlg

#import fdf_base as fdf
import wx.lib.agw.ultimatelistctrl as ulc

'A class collection representing extra options panel'


class ExtraPN(wx.ScrolledWindow):
    
    blocks = {}
    
    def __init__(self, *args, **kwds):
        wx.ScrolledWindow.__init__(self, *args, **kwds)
        
        self.OptL = wx.StaticText(self, -1, 'Option')
        self.ValL = wx.StaticText(self, -1, 'Value')
        self.OptTE = wx.TextCtrl(self, -1)
        self.ValTE = wx.TextCtrl(self, -1)
        
        self.ExtraList = ulc.UltimateListCtrl(self, -1, agwStyle=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES |
                                              ulc.ULC_HAS_VARIABLE_ROW_HEIGHT)
        
        self.AddBtn = wx.Button(self, -1, 'Add')
        self.AddBlockBtn = wx.Button(self, -1, 'Add block')
        self.RmBtn = wx.Button(self, -1, 'Remove')
        
        self.fdf_opts = {}

        #binding events
        self.Bind(wx.EVT_BUTTON, self.OnAddBtn, self.AddBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAddBlockBtn, self.AddBlockBtn)
        self.Bind(wx.EVT_BUTTON, self.OnRmBtn, self.RmBtn)
        
        self.__set_properties()
        self.__do_layout()

    def OnAddBtn(self, evt):
        # add value
        if self.OptTE.GetValue() and self.ValTE.GetValue():
            ind = self.ExtraList.InsertStringItem(sys.maxint, self.OptTE.GetValue())
            self.ExtraList.SetStringItem(ind, 1, self.ValTE.GetValue())
            self.OptTE.SetValue('') 
            self.ValTE.SetValue('')
    
    def OnRmBtn(self, evt):
        # delete item
        for _ in range(self.ExtraList.GetSelectedItemCount()):
            row = self.ExtraList.GetFirstSelected()
            # delete from blocks if block is being deleted
            if self.ExtraList.GetItem(row,0).GetText() in self.blocks.keys():
                opt = self.ExtraList.GetItem(row,0).GetText()
                # unbind button
                self.Unbind(wx.EVT_BUTTON, self.blocks[opt][0])
                # destroy button
                self.blocks[opt][0].Destroy()
                # pop from blocks
                self.blocks.pop(opt)
            self.ExtraList.DeleteItem(row)

    def OnAddBlockBtn(self, evt):
        # add block
        dlg = AddBlockDlg(self, def_opt = self.OptTE.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            opt, val = dlg.GetBlock()
            self.add_block(opt, val)
        dlg.Destroy()
    
    def OnShowBtn(self, evt):
        for old_opt, [btn, old_val] in self.blocks.iteritems():
            btn_id = btn.GetId()
            if btn_id == evt.GetId():
                # allow to change option and value via dlg
                dlg = AddBlockDlg(self, def_opt = old_opt, def_val = old_val)
                if dlg.ShowModal() == wx.ID_OK:
                    # delete old_opt
                    self.blocks.pop(old_opt)
                    # insert new_opt
                    new_opt, new_val = dlg.GetBlock()
                    self.blocks[new_opt] = [btn, new_val] 
                    # change value in list 
                    item, = [i for i in range(self.ExtraList.GetItemCount()) if self.ExtraList.GetItem(i, 0).GetText() == old_opt]
                    self.ExtraList.SetStringItem(item, 0, new_opt) 
                dlg.Destroy()
                break 
    
    def add_block(self, opt, val):
        # 'show' button
        show_btn = wx.Button(self.ExtraList, -1, 'Show')
        # add to blocks
        self.blocks[opt] = [show_btn, val]
        # add to list
        ind = self.ExtraList.InsertStringItem(sys.maxint, opt)
        self.ExtraList.SetItemWindow(ind, 1, show_btn, expand=True)
        # bind show_btn
        self.Bind(wx.EVT_BUTTON, self.OnShowBtn, show_btn)
    
    def populate(self, d):
        'Populates extras pane with values from fdf dictionary'
        for key, t_val in d.iteritems():
            try:
                if t_val.__class__.__name__ == 'BlockValue':
                    self.add_block(key, '\n'.join([' '.join(s) for s in t_val.value]))
                else:
                    ind = self.ExtraList.InsertStringItem(sys.maxint, key)
                    self.ExtraList.SetStringItem(ind, 1, str(t_val))
            except IndexError:
                continue

    def extract(self):
        s = ""
        items = []
        for i in range(self.ExtraList.GetItemCount()):
            items.append([self.ExtraList.GetItem(itemOrId=i, col=j).GetText() for j in range(2)])
        for k, v in items:
            if k in self.blocks:
                s += ("%block {0}\n"
                      "  {1}\n"
                      "%endblock {0}\n").format(k, self.blocks[k][1])
            else:
                s += "{0:<25}\t{1}\n".format(k, v)
        return s
    
    def __set_properties(self):
        self.SetScrollRate(0, 10)
        self.ExtraList.InsertColumn(0, 'Option', width = 250)
        self.ExtraList.InsertColumn(1, 'Value', width = 400)

    def __do_layout(self):
        opt_sizer = wx.GridSizer(rows=2, cols=2, vgap=5, hgap=5)
        opt_sizer.Add(self.OptL, 0, wx.ALL|wx.ALIGN_CENTER, 0)
        opt_sizer.Add(self.ValL, 0, wx.ALL|wx.ALIGN_CENTER, 0)
        opt_sizer.Add(self.OptTE, 1, wx.ALL|wx.EXPAND, 0)
        opt_sizer.Add(self.ValTE, 1, wx.ALL|wx.EXPAND, 0)
        
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.AddBtn, 0, wx.ALL, 5)
        btn_sizer.Add(self.AddBlockBtn, 0, wx.ALL, 5)
        btn_sizer.Add(self.RmBtn, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(opt_sizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn_sizer, 0, wx.ALL, 0)
        sizer.Add(self.ExtraList, 1, wx.ALL|wx.EXPAND, 5)

        self.SetSizer(sizer)
        self.Layout()

if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    f = wx.Frame(None, -1)
    p = ExtraPN(f, -1)

    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(p, 1, wx.EXPAND, 0)
    f.SetSizer(s)
    f.Layout()
    app.SetTopWindow(f)
    f.Show()
    app.MainLoop()
