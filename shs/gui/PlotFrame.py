# -*- coding: utf-8 -*-

import math
import os
import wx
from wx.lib.mixins.listctrl import getListCtrlSelection
try:
    from wx.lib.pubsub.pub import Publisher
except ImportError:
    from wx.lib.pubsub import pub

import matplotlib.cm as cm
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.backends.backend_wx import \
    _load_bitmap

from FitDialog import FitDialog
import fit
import mbox

class MyCustomToolbar(NavigationToolbar):
    EXPORT_DATA = wx.NewId()
    
    def __init__(self, plotCanvas):
        # create the default toolbar
        NavigationToolbar.__init__(self, plotCanvas)
        # find where icons are located
        path = os.path.dirname(__file__)
        icon_file = os.path.join(path, 'data-export-icon.png')
        self.AddSimpleTool(self.EXPORT_DATA, _load_bitmap(icon_file),
                           'Export data', 'Export current data to file')
        wx.EVT_TOOL(self, self.EXPORT_DATA, self._on_export_data)
        
    def _on_export_data(self, evt):
        if not hasattr(self, 'dirname'):
            self.dirname = os.path.expanduser('~')
        dlg = wx.DirDialog(self, "Choose a directory to export data to", self.dirname,  wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()
        else:
            dlg.Destroy()
            return 1
        dlg.Destroy()        
# write each axis data in separate file
        for axis in self.canvas.figure.get_axes():
# axis title - the name of the file
            title = axis.get_title()
            l = [t.get_text() for t in self.canvas.figure.legends[0].get_texts()]
            if os.sep in l[0]:
                l = [t.split(os.sep) for t in l]
                l = ['.'.join(t[1:3]) for t in l]
            
# getting data            
            x_max = 0
            y = []
            for line in axis.get_lines():
                x_c = len(line.get_xdata()) 
                if x_c > x_max:
                    x_max = x_c
                    x = line.get_xdata()
                y.append(line.get_ydata())
# printing data to file
            f = open(os.path.join(self.dirname, title.replace('/','_') + '.dat'), 'w')
            
            head = ['   X   '] + l
            hl = [len(t) for t in l]
            hf = '{0[0]:7} ' 
            for i in range(1, len(l) + 1):
                hf += ' {0[%i]:%i} ' % (i, hl[i-1])
            f.write(hf.format(head) + '\n')
            y_max = [len(yi) for yi in y]
            for xi in range(x_max):
                is_y = [yi > xi for yi in y_max]
                data = [x[xi]]
                df = '{0[0]:^7.3f} '
                for yi, is_yi in enumerate(is_y):
                    if is_yi:
                        data.append(y[yi][xi])
                        df += ' {0[%i]:^%i.5f} ' % (len(data) - 1, hl[yi-1])
                    else:
                        df += ' ' * (hl[yi-1] + 2)
                f.write(df.format(data) + '\n')
            f.close()
        mbox.DataExported(self.dirname)

class PlotFrame(wx.Frame):
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: PlotFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.CreateMplFigure()
        self.PlotsCtrl = wx.ListCtrl(self.panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.ByCalcsChkBox = wx.CheckBox(self.panel, -1, 'Group by calcs')
        self.ReplotBtn = wx.Button(self.panel, -1, "Replot!")
        self.ShowInfoBtn = wx.Button(self.panel, -1, "Show info") 
        self.FitBtn = wx.Button(self.panel, -1, "Begin fit")
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.ReplotBtnPress, self.ReplotBtn)
        self.Bind(wx.EVT_BUTTON, self.InfoBtnPress, self.ShowInfoBtn)
        self.Bind(wx.EVT_BUTTON, self.FitBtnPress, self.FitBtn)
        self.Bind(wx.EVT_CHECKBOX, self.ByCalcsCheck, self.ByCalcsChkBox)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Center()
        # end wxGlade
        self.PlotsCtrl.InsertColumn(0,'Data', width = 100)

    def CreateMplFigure(self):
        self.panel = wx.Panel(self)

        self.dpi = 100
        self.fig = Figure((8.0, 6.4), dpi=self.dpi)
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.axes = self.fig.add_subplot(111)
        self.toolbar = MyCustomToolbar(self.canvas)

    def __set_properties(self):
        self.fitting = False
        self.fit_points = []
        self.SetTitle(self.title)
    
    def __do_layout(self):
        PCSizer = wx.BoxSizer(wx.VERTICAL)
        PCSizer.Add(self.ByCalcsChkBox, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        PCSizer.Add(self.ReplotBtn, 0, wx.ALL | wx.EXPAND, 5)
        PCSizer.Add(self.PlotsCtrl, 1, wx.ALL |wx.EXPAND, 5)
        PCSizer.Add(self.ShowInfoBtn, 0, wx.ALL |wx.EXPAND, 5)
        PCSizer.Add(self.FitBtn, 0, wx.ALL |wx.EXPAND, 5)
        PCSizer.Add((30, 30), 1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        vbox.Add(self.toolbar, 0, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(PCSizer, 0, wx.ALL | wx.EXPAND, 5)
        hbox.Add(vbox, 1, wx.ALL | wx.EXPAND, 5)

        self.panel.SetSizer(hbox)
        hbox.Fit(self)

# Methods to be implemented in subclasses    
    def ReplotBtnPress(self, evt):
        self.replot()

    def InfoBtnPress(self, event):
        pass

    def FitBtnPress(self, event):
        pass

    def ByCalcsCheck(self, event):
        self.initplot()
        self.replot()

    def OnClose(self, event):
        pass

class PlotFuncFrame(PlotFrame):
    title = 'Plot'

    def __init__(self, *args, **kwds):
        PlotFrame.__init__(self, *args, **kwds)
        pub.subscribe(self.plot, 'data.plot')

    def plot(self, message):
        self.data = message
        self.initplot()
        self.replot()

    def initplot(self):
        self.PlotsCtrl.DeleteAllItems()
        # all data are the same for different calcs
        assert len(set([d.y_titles for d in self.data])) == 1
        # graphs - different graphs
        # leg - different lines on a graph
        if self.ByCalcsChkBox.IsChecked():
            graphs = [d.title for d in self.data]
            self.leg = self.data[0].y_titles
        else:
            graphs = self.data[0].y_titles
            self.leg = [d.title for d in self.data]
        for i, s in enumerate(graphs):
            self.PlotsCtrl.InsertStringItem(i, s)
        # adjusting column width
        self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER) 
        wh = self.PlotsCtrl.GetColumnWidth(0); 
        self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE) 
        wc = self.PlotsCtrl.GetColumnWidth(0); 
        if wh > wc: 
            self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER) 

        self.PlotsCtrl.Select(0, 1)

    def replot(self, cfd = True):
        sind = getListCtrlSelection(self.PlotsCtrl)
        print sind
        ng = len(sind)
        ncols = round(ng**0.5)
        if ncols == 0.:
            ncols = 1.
        nrows = math.ceil(ng / ncols)
        self.fig.clear()
        # clear fitting data as well
        if cfd:
            self.fit_points = []
        self.FitBtn.SetLabel("Begin fit")
        self.fitting = False

        for i, igraph in enumerate(sind):
            title = self.PlotsCtrl.GetItemText(igraph)
            axes = self.fig.add_subplot(nrows,ncols,i+1)
            axes.set_title(title)
            if self.ByCalcsChkBox.IsChecked():
                if not hasattr(self.data[igraph],'var_x'):
                    x = self.data[igraph].x
                else:
                    x = range(len(self.data[igraph].x))
                    axes.get_xaxis().set_ticks(x)
                    axes.get_xaxis().set_ticklabels(self.data[igraph].x, rotation=60, size='x-small')
                for y in self.data[igraph].y:
                    axes.plot(x, y)
            else:
                for d in self.data:
                    if not hasattr(d,'var_x'):
                        x = d.x
                    else:
                        x = range(len(d.x))
                        axes.get_xaxis().set_ticks(x) 
                        axes.get_xaxis().set_ticklabels(d.x, rotation=60, size='x-small') 
                    axes.plot(x, d.y[igraph])
        # get legend
        lines = self.fig.axes[0].get_lines()
        self.fig.legend(lines, self.leg, 1)
        self.fig.tight_layout()
        self.canvas.draw()

    def InfoBtnPress(self, evt):
        if self.info is None:
            mbox.NoInfo()
            return 1
        mbox.ShowPlotInfo(self.calcs, self.info)

    def FitBtnPress(self, evt):
        sind = getListCtrlSelection(self.PlotsCtrl)
        if len(sind) > 1:
            print 'There should be one axis!'
            return
        sind = sind[0]
        
        if not self.fitting:
            # begin fit; show dialog
            dlg = FitDialog(self, sets = self.leg)
            if not dlg.ShowModal() == wx.ID_OK:
                dlg.Destroy()
                return
            # get data from dialog
            opts, iset = dlg.GetFitOptions()
            dlg.Destroy()
            # some quirks to begin fitting
            self.FitBtn.SetLabel("Finish fit")
            self.fitting = True
            self.canvas.Bind(wx.EVT_LEFT_DCLICK, self.OnCanvasClick)
            # get fit set according to the state of GBC checkbox
            if self.ByCalcsChkBox.IsChecked():
                fit_set = (self.data[sind][self.x], self.data[sind][self.PlotsCtrl.GetItemText(iset)])
            else:
                fit_set = (self.data[iset][self.x], self.data[iset][self.PlotsCtrl.GetItemText(sind)])
            self.fit = fit.Fit(opts, fit_set) 
        else:
            # try to end fit
            if not self.fit.is_enough(len(self.fit_points)):
                return
            self.canvas.Unbind(wx.EVT_LEFT_DCLICK)
# fitting itself
            p, x, y = self.fit.fit(self.fit_points)
            self.replot()
            ax = self.fig.gca()
            ax.plot(x, y, '--x')
            self.canvas.draw()
            self.AddFitInfo(self.fit.FitInfo())
        
    def OnCanvasClick(self, evt):
        if self.fit.is_enough(len(self.fit_points)):
            self.canvas.Unbind(wx.EVT_LEFT_DCLICK)
            return
        ax = self.fig.gca()
        p = ax.transData.inverted().transform(evt.GetPositionTuple())
        ax.axvline(x = p[0], c = 'r')
        self.fit_points.append(p[0])
        print 'Selected x = %f' % (p[0])
        self.canvas.draw()
        
        
    def AddFitInfo(self, info):
        'Adds fitting info to self.info'
        print info
    
    def OnClose(self, evt):
        pub.unsubscribe(self.plot, 'data.plot')
        self.Destroy()

# end of class PlotFrame

class PlotCorrFrame(PlotFrame):
    title = 'Correlations'

    def __init__(self, *args, **kwds):
        PlotFrame.__init__(self, *args, **kwds)
        pub.subscribe(self.plot, 'corr.plot')
    
    def plot(self, message):
        self.calcs = message[0]
        self.data = message[1]
        # a number of tuples (x, y1, ... yn)
        # self.names = self.data[0][1].dtype.names
        self.names = message[2]
        self.initplot()
        self.replot()       

    def initplot(self):
        self.PlotsCtrl.DeleteAllItems()
        if self.ByCalcsChkBox.IsChecked():
            data = self.calcs
            self.leg = self.names
        else:
            data = self.names
            self.leg = self.calcs
        for i, s in enumerate(data):
            self.PlotsCtrl.InsertStringItem(i, s)
        # adjusting column width
        self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER) 
        wh = self.PlotsCtrl.GetColumnWidth(0); 
        self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE) 
        wc = self.PlotsCtrl.GetColumnWidth(0); 
        if wh > wc: 
            self.PlotsCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER) 
        
        self.PlotsCtrl.Select(0, 1)

    def replot(self):
        sind = getListCtrlSelection(self.PlotsCtrl)
        ng = len(sind)
        ncols = round(ng**0.5)
        if ncols == 0.:
            ncols = 1.
        nrows = math.ceil(ng / ncols)
        self.fig.clear()
        
        for i, igraph in enumerate(sind):
            color = iter(cm.get_cmap('prism')([x/24. for x in range(24)]))
            title = self.PlotsCtrl.GetItemText(igraph)
            axes = self.fig.add_subplot(nrows,ncols,i+1)
            axes.set_title(title)
            sdata = []
            if self.ByCalcsChkBox.IsChecked():
                for ins in range(len(self.names)):
                    sdata.append(axes.scatter(self.data[igraph][ins][0], self.data[igraph][ins][1], c = next(color)))
            else:
                for ds in self.data:
                    sdata.append(axes.scatter(ds[igraph][0], ds[igraph][1], c = next(color)))
                    
        # get legend
        self.fig.legend(sdata, self.leg, scatterpoints = 1)
        self.canvas.draw()

    def OnClose(self, evt):
        Publisher().unsubscribe(self.plot,('corr.plot'))
        self.Destroy()
