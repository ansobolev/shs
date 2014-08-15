# -*- coding: utf-8 -*-
import wx
from wx.wizard import WizardPageSimple
from wx.lib.mixins.listctrl import getListCtrlSelection
from fillin_page import FillInNBPage
from ..fdf_options import ChoiceLine


class SelectPage(WizardPageSimple):
    def __init__(self, parent):
        self.parent = parent
        WizardPageSimple.__init__(self, parent)
        self.selected_options = []
        self.LabelText = wx.StaticText(self, -1, label="Select FDF options to include in batch run:")
        self.OptionsTree = wx.TreeCtrl(self, -1, style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.SelectBtn = wx.Button(self, -1, ">>")
        self.DeselectBtn = wx.Button(self, -1, "<<")
        self.OptionsList = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
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
                option_text = self.selected_options.pop(si - ds)
                self.OptionsList.DeleteItem(si - ds)
                self.parent.remove_FDF_option(option_text)
                ds += 1
            return 0
        return 1

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.OptionsTree, 1, wx.EXPAND | wx.ALL, 5)
        btn_sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer.Add(self.SelectBtn, 0, wx.EXPAND | wx.ALL, 2)
        btn_sizer.Add(self.DeselectBtn, 0, wx.EXPAND | wx.ALL, 2)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 3)
        main_sizer.Add(self.OptionsList, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, 0)
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
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_Notebook, self.Notebook)
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
        if not self.RemoveBtn.IsEnabled():
            self.RemoveBtn.Enable(True)
        cls = self.parent.get_option_class(page_name)
        option = cls(page, optional=False)
        page.add_option(option)
        self.parent.add_value(page_name, option)

    def on_RemoveBtn(self, evt):
        idx = self.Notebook.GetSelection()
        page_name = self.page_names[idx]
        page = self.pages[idx]
        page.remove_option()
        if len(page) == 0:
            self.RemoveBtn.Enable(False)
        self.parent.remove_value(page_name)

    def on_Notebook(self, evt):
        idx = evt.GetSelection()
        page = self.pages[idx]
        self.RemoveBtn.Enable(len(page))

    def __set_properties(self):
        self.RemoveBtn.Enable(False)

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.Notebook, 1, wx.EXPAND | wx.ALL, 5)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.AddBtn, 0, wx.EXPAND | wx.ALL, 2)
        btn_sizer.Add(self.RemoveBtn, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(sizer)


class DDTreeCtrl(wx.TreeCtrl):
    """ Drag'n'drop enabled subclass of wxPython TreeCtrl
    (from http://wiki.wxpython.org/DragAndDropWithFolderMovingAndRearranging, with some changes)
    """

    def __init__(self, *args, **kwds):
        wx.TreeCtrl.__init__(self, *args, **kwds)

    def traverse(self, func, start):
        """Apply 'func' to each node in a branch, beginning with 'start'. """

        def traverse_aux(node, depth, func):
            nc = self.GetChildrenCount(node, 0)
            child, cookie = self.GetFirstChild(node)
            # In wxPython 2.5.4, GetFirstChild only takes 1 argument
            for i in xrange(nc):
                func(child, depth)
                traverse_aux(child, depth + 1, func)
                child, cookie = self.GetNextChild(node, cookie)

        func(start, 0)
        traverse_aux(start, 1, func)

    def item_is_child_of(self, item1, item2):
        """ Tests if item1 is a child of item2, using the traverse function """
        def check_parent(parent, item):
            if not parent.IsOk():
                return False
            elif parent == item:
                return True
            else:
                return check_parent(self.GetItemParent(parent), item)

        return check_parent(item1, item2)

    def save_items_to_list(self, start):
        """ Generates a python object representation of the tree (or a branch of it),
            composed of a list of dictionaries with the following key/values:
            label:      the text that the tree item had
            children:   a list containing the node's children (one of these dictionaries for each)
        """
        result = []

        def save_func(node, depth):
            tmp_result = result
            for x in range(depth):
                if type(tmp_result[-1]) is not dict:
                    tmp_result.append({})
                tmp_result = tmp_result[-1].setdefault('children', [])

            item = {'label': self.GetItemText(node)}
            tmp_result.append(item)
        self.traverse(save_func, start)
        return result

    def insert_items_from_list(self, item_list, parent, insert_after=None, append_after=False):
        """ Takes a list, 'item_list', generated by save_items_to_list, and inserts
            it in to the tree. The items are inserted as children of the
            tree item given by 'parent', and if 'insert_after' is specified, they
            are inserted directly after that tree item. Otherwise, they are put at
            the beginning.

            If 'append_after' is True, each item is appended. Otherwise it is prepended.
            In the case of children, you want to append them to keep them in the same order.
            However, to put an item at the start of a branch that has children, you need to
            use prepend. (This will need modification for multiple inserts. Probably reverse
            the list.)

            Returns a list of the newly inserted tree_items, so they can be
            selected, etc..
        """
        new_items = {}
        for item in item_list:
            if insert_after:
                node = self.InsertItem(parent, insert_after, item['label'])
            elif append_after:
                node = self.AppendItem(parent, item['label'])
            else:
                node = self.PrependItem(parent, item['label'])

            new_items[item['label']] = node
            if 'children' in item:
                new_items.update(self.insert_items_from_list(item['children'], node, append_after=True))
        return new_items

    def GetLevel(self, node):
        parent = self.GetItemParent(node)
        if not parent.IsOk():
            return 0
        else:
            return 1 + self.GetLevel(parent)


class DirHierarchyPage(WizardPageSimple):
    def __init__(self, parent):
        self.parent = parent
        self.drag_item_list = None
        WizardPageSimple.__init__(self, parent)
        self.LabelText = wx.StaticText(self, -1, label="Drag and drop FDF options in a tree to create selected "
                                                       "directory hierarchy:")
        self.DirTree = DDTreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS)
        self.ids = {'root': self.DirTree.AddRoot('Root directory')}
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag_begin, self.DirTree)
        self.Bind(wx.EVT_TREE_END_DRAG, self.on_drag_end, self.DirTree)
        self.__set_properties()
        self.__do_layout()

    def add_FDF_option(self, option):
        self.ids[option] = self.DirTree.AppendItem(self.ids['root'], option)
        self.DirTree.ExpandAll()

    def remove_FDF_option(self, option):
        item = self.ids.pop(option)
        parent = self.DirTree.GetItemParent(item)
        children = self.DirTree.save_items_to_list(item)[0].get('children', [])
        self.DirTree.Delete(item)
        if len(children) != 0:
            new_nodes = self.DirTree.insert_items_from_list(children, parent)
            self.ids.update(new_nodes)
            for label, node in new_nodes.iteritems():
                level = self.DirTree.GetLevel(node)
                self.parent.alter_level(label, level)

    def on_drag_begin(self, evt):
        evt.Allow()
        self.drag_item_list = self.DirTree.save_items_to_list(evt.GetItem())

    def on_drag_end(self, evt):
        # If we dropped somewhere that isn't on top of an item, ignore the event
        if not evt.GetItem().IsOk():
            return
        # Make sure this member exists.
        old = self.ids[self.drag_item_list[0]['label']]
        # Get the other IDs that are involved
        new = evt.GetItem()
        if self.DirTree.item_is_child_of(new, old):
            return
        # Move 'em
        self.DirTree.Delete(old)
        new_nodes = self.DirTree.insert_items_from_list(self.drag_item_list, new)
        self.ids.update(new_nodes)
        for label, node in new_nodes.iteritems():
            level = self.DirTree.GetLevel(node)
            self.parent.alter_level(label, level)
        self.DirTree.ExpandAll()
        print self.parent.values

    def __set_properties(self):
        pass

    def __do_layout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.LabelText, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.DirTree, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()


class DirNamePage(WizardPageSimple):

    class LevelLine(ChoiceLine):
        label = "Level"

        def __init__(self, *args, **kwds):
            self.choices = ["Ordinal numbers", ]
            ChoiceLine.__init__(self, *args, **kwds)

        def append_choice(self, choice):
            self._sizer.value.AppendChoice(choice)

        def delete_choice(self, choice):
            self._sizer.value.DeleteChoice(choice)

        def get_count(self):
            return self._sizer.value.GetCount()

    def __init__(self, parent):
        self.parent = parent
        self._sizer = None
        self._levels = []
        WizardPageSimple.__init__(self, parent)
        self.LabelText = wx.StaticText(self, -1, label="Select titles of directories on selected levels:")
        self.__set_properties()
        self.__do_layout()

    def add_to_level(self, choice, level):
        if len(self._levels) < level:
            self.add_level()
        level_line = self._levels[level-1]
        level_line.append_choice(choice)

    def remove_from_level(self, choice, level):
        level_line = self._levels[level-1]
        level_line.delete_choice(choice)
        if level == len(self._levels) and level_line.get_count() == 1:
            self.remove_level(level)

    def move_between_levels(self, choice, l1,l2):
        self.add_to_level(choice, l2)
        self.remove_from_level(choice, l1)

    def add_level(self):
        level = self.LevelLine(self)
        self._levels.append(level)
        i_level = len(self._levels)
        level._sizer.SetLabel("Level %i" % (i_level, ))
        self._sizer.Add(level.sizer, 0, wx.EXPAND | wx.ALL, 5)

    def remove_level(self, i_level):
        assert i_level == len(self._levels)
        level = self._levels.pop(i_level-1)
        self._sizer.Hide(i_level)
        self._sizer.Remove(i_level)
        self.Layout()

    def __set_properties(self):
        pass

    def __do_layout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.LabelText, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self._sizer)
        self.Layout()