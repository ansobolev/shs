
import os
import wx
import functools
import pkgutil
import inspect
from collections import OrderedDict

from shs.sio import FDFFile
from shs.options import Options
from shs.geom import Geom

from .. import panels
from ..fdf_optionlist import FDFOptionList
from ..dialogs.batch import BatchWizard
from init_panel import NBPage
from extra_panel import ExtraPN

class MainFrame(wx.Frame):

    def __init__(self, *args, **kwds):
        panels_list = []
        self.ol = OrderedDict()
        self.fdf_ol = OrderedDict()
        for importer, modname, _ in pkgutil.iter_modules(panels.__path__):
            loader = importer.find_module(modname)
            module = loader.load_module(modname)
            panels_list.append(module)
        panels_list.sort(key = lambda panel: panel.__page__)
        wx.Frame.__init__(self, *args, **kwds)
        self.NB = wx.Notebook(self, -1, style = 0)
        for panel in panels_list:
            page = NBPage(self.NB, -1, panel=panel)
            self.NB.AddPage(page, panel.__title__)
            self.ol.update(page.ol.ol)
            self.fdf_ol[panel.__title__] = page.ol.fdf_ol
        # create extra notebook page
        self.extra_page = ExtraPN(self.NB, -1)
        self.NB.AddPage(self.extra_page, 'Extra')

        # create buttons
        self.ImportBtn = wx.Button(self, -1, 'Import...')
        self.ExportBtn = wx.Button(self, -1, 'Export...')
        self.BatchBtn = wx.Button(self, -1, 'Batch')

        self.__create_bindings()
        self.__set_properties()
        self.__do_layout()

    def __create_bindings(self):
        # create bindings for buttons
        self.Bind(wx.EVT_BUTTON, self.on_import, self.ImportBtn)
        self.Bind(wx.EVT_BUTTON, self.on_export, self.ExportBtn)
        self.Bind(wx.EVT_BUTTON, self.on_batch, self.BatchBtn)

        # ceate bindings for notebook fdf options
        for (name, value) in self.ol.iteritems():
            if value.bindings is not None:
                for (widget, event, fun) in value.bindings:
                    fun_args = inspect.getargspec(fun).args
                    if len(fun_args) > 2:
                        kwds = {}
                        for fun_arg in fun_args[2:]:
                            kwds[fun_arg] = self.ol[fun_arg]
                        fun = functools.partial(fun, **kwds)
                    self.Bind(event, fun, widget)


    def __set_properties(self):
        pass

    def __do_layout(self):

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

    def on_import(self, event):
        'Gets FDF file dictionary'
        dlg = wx.FileDialog(self, 'Choose FDF file to import', wildcard = '*.fdf', style = wx.ID_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            fdfn = dlg.GetPath()
            fdff = FDFFile(fdfn)
            # get options 
            fdfo = Options(fdff.d)
            self.import_FDF(fdfo.opts)
        dlg.Destroy()

    def on_export(self, event):
        'Exports FDF file dictionary to file'
        dlg = wx.FileDialog(self, 'Choose FDF file to export to', wildcard = '*.fdf', style = wx.ID_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            fdfn = dlg.GetPath()
            self.export_FDF(fdfn)
        dlg.Destroy()

    def on_batch(self, event):
        'Runs batch wizard'
        wiz = BatchWizard(self, -1, options=self.fdf_ol)
        wiz.run()
        wiz.Destroy()

    def import_FDF(self, d):
        'Imports FDF dictionary to shs-init'
        for option, value in d.items():
            if option.lower() in self.fdf_ol.keys():
                self.fdf_ol[option.lower()].SetFDFValue(value)
                d.pop(option)
        # all remaining options go to extras
        self.extra_page.Populate(d)

    def export_FDF(self, fname):
        with open(fname, 'w') as f:
            for _, v in self.fdf_ol.iteritems():
                print v.fdf_text, v.value
