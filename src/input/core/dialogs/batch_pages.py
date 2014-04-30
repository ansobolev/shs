# -*- coding: utf-8 -*-
import wx
from wx.wizard import PyWizardPage, WizardPage, WizardPageSimple
from wx.lib.mixins.listctrl import getListCtrlSelection
from fillin_page import FillInNBPage

class SelectPage(WizardPageSimple):

    def __init__(self, parent):
        self.parent = parent
        WizardPageSimple.__init__(self, parent)
        self.selected_options = []
        self.LabelText = wx.StaticText(self, -1, label="Select FDF options to include in batch run:")
        self.OptionsTree = wx.TreeCtrl(self, -1, style=wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        self.SelectBtn = wx.Button(self, -1, ">>")
        self.DeselectBtn = wx.Button(self, -1, "<<")
        self.OptionsList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        # initialize OptionsList
        self.OptionsList.InsertColumn(0, 'Options', width=180)
        # binding events
        self.Bind(wx.EVT_BUTTON, self.on_SelectBtn, self.SelectBtn)
        self.Bind(wx.EVT_BUTTON, self.on_DeselectBtn, self.DeselectBtn)
        self.__set_properties()
        self.__do_layout()

    def build_tree(self, options):
        self.OptionsTree.DeleteAllItems()
        ids = {'root': self.OptionsTree.AddRoot('root')}
        for (panel, options) in options.iteritems():
            ids[panel] = self.OptionsTree.AppendItem(ids['root'], panel)
            for (option, instance) in options.iteritems():
                if type(instance.fdf_text) == list:
                    for t in instance.fdf_text:
                        if t.lower() == option:
                            self.OptionsTree.AppendItem(ids[panel], t)
                else:
                    self.OptionsTree.AppendItem(ids[panel], instance.fdf_text)

    def on_SelectBtn(self, evt):
        item = self.OptionsTree.GetSelection()
        # see if we selected root itself or panel name; its parent is root
        text = self.OptionsTree.GetItemText(item)
        if text == 'root':
            return None
        if text in self.selected_options:
            print 'You have chosen this option already!'
            return None
        parent = self.OptionsTree.GetItemParent(item)
        if self.OptionsTree.GetItemText(parent) == 'root': 
            print 'The panel name cannot be selected!'
            return None
        clc = self.OptionsList.GetItemCount()
        self.OptionsList.InsertStringItem(clc, text)
        self.selected_options.append(text)
        self.parent.add_FDF_option(text)

    def on_DeselectBtn(self, evt):
        sind = getListCtrlSelection(self.OptionsList)
        if sind:
            ds = 0
            for si in sind:
                option_text = self.selected_options.pop(si-ds)
                self.OptionsList.DeleteItem(si-ds)
                self.parent.remove_FDF_option(option_text)
                ds += 1
            return 0
        return 1

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND|wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.OptionsTree, 1, wx.EXPAND|wx.ALL, 5)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(self.SelectBtn, 0, wx.EXPAND|wx.ALL, 2)
        btn_sizer.Add(self.DeselectBtn, 0, wx.EXPAND|wx.ALL, 2)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 3)
        main_sizer.Add(self.OptionsList, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(main_sizer, 1, wx.EXPAND|wx.ALL, 0)        
        self.SetSizer(sizer)

class FillInPage(WizardPageSimple):

    def __init__(self, parent):
        self.parent = parent
        self.page_names = []
        self.pages = []
        WizardPageSimple.__init__(self, parent)
        self.LabelText = wx.StaticText(self, -1, label="Add values to selected FDF options:")
        self.Notebook = wx.Notebook(self, -1, style=wx.NB_TOP)
        self.AddBtn = wx.Button(self, -1, "Add")
        self.RemoveBtn = wx.Button(self, -1, "Remove")
        # binding events
        self.Bind(wx.EVT_BUTTON, self.on_AddBtn, self.AddBtn)
        self.Bind(wx.EVT_BUTTON, self.on_RemoveBtn, self.RemoveBtn)
        self.__set_properties()
        self.__do_layout()

    def add_FDF_option(self, option):
        page = FillInNBPage(self.Notebook, -1)
        self.page_names.append(option)
        self.pages.append(page)
        self.Notebook.AddPage(page, option)

    def remove_FDF_option(self, option):
        pidx = self.page_names.index(option)
        self.page_names.pop(pidx)
        self.pages.pop(pidx)
        self.Notebook.DeletePage(pidx)

    def on_AddBtn(self, evt):
        idx = self.Notebook.GetSelection()
        page_name = self.page_names[idx]
        page = self.pages[idx]
        cls = self.parent.get_option_class(page_name)
        option = cls(page)
        page.add_option(option)

    def on_RemoveBtn(self, evt):
        pass

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND|wx.ALL, 0)
        sizer.Add(self.Notebook, 1, wx.EXPAND|wx.ALL, 5)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.AddBtn, 0, wx.EXPAND|wx.ALL, 2)
        btn_sizer.Add(self.RemoveBtn, 0, wx.EXPAND|wx.ALL, 2)
        sizer.Add(btn_sizer, 0, wx.EXPAND|wx.ALL, 3)
        self.SetSizer(sizer)

class DirHierarchyPage(WizardPageSimple):

    def __init__(self, parent):
        self.parent = parent
        WizardPageSimple.__init__(self, parent)
        self.LabelText = wx.StaticText(self, -1, label="Drag and drop FDF options in a tree to create selected directory hierarchy:")
        self.DirTree = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS)
        self.ids = {'root': self.DirTree.AddRoot('Root directory')}
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag_begin, self.DirTree)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_drag_end, self.DirTree)
        self.__set_properties()
        self.__do_layout()

    def add_FDF_option(self, option):
        self.ids[option] = self.DirTree.AppendItem(self.ids['root'], option)
        self.DirTree.ExpandAll()

    def remove_FDF_option(self, option):
        pass

    def on_drag_begin(self, evt):
        if self.DirTree.GetChildrenCount(evt.GetItem()) == 0:
            evt.Allow()
            self.drag_item = evt.GetItem()
        else:
            print "You can't drag item with children to anywhere!"
    
    def on_drag_end(self, evt):
        #If we dropped somewhere that isn't on top of an item, ignore the event
        if not evt.GetItem().IsOk():
            return
        # Make sure this memeber exists.
        try:
            old = self.drag_item
        except:
            return
        # Get the other IDs that are involved
        new = evt.GetItem()
        # Move 'em
        text = self.DirTree.GetItemText(old)
        self.DirTree.Delete(old)
        self.DirTree.AppendItem(new, text)
        self.DirTree.ExpandAll()

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND|wx.ALL, 0)
        sizer.Add(self.DirTree, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()
