# -*- coding: utf-8 -*-
# generated by wxGlade HG on Fri Jan 13 14:51:14 2012

import os, time, subprocess
import wx
from wx.lib.mixins.listctrl import getListCtrlSelection
from wx.lib.pubsub import Publisher 

import StepsDialog as SD, PlotFrame as PF, CorrDialog as CD
import interface
import mbox

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode

# end wxGlade

class RootFrame(wx.Frame):
    
    if os.path.exists('/home/physics/calc'):
        root = '/home/physics/calc'
    else:
        root = '/home/andrey/calc'
 
    calcs = []
    
    def __init__(self, *args, **kwds):
        # begin wxGlade: RootFrame.__init__
        self.searchString = ""
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.CalcTree = wx.TreeCtrl(self, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_HIDE_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.TypeRBox = wx.RadioBox(self, -1, "Type", choices=[".FDF", ".ANI", ".output", "pdos.xml"], majorDimension=4, style=wx.RA_HORIZONTAL)
        self.DownBtn = wx.Button(self, -1, ">>")
        self.UpBtn = wx.Button(self, -1, "<<")
        self.GetData = wx.Button(self, -1, "Get calc data")
        self.btnEnqueue = wx.Button(self, -1, "Enqueue job")
        self.CalcList = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.PropType = wx.Choice(self, -1, choices=["Function","Histogram","Time evolution"]) 
        self.propChoices = {"function": ["Run evolution (MDE)","Partial RDFs","Selfdiffusion (MSD)","Velocity autocorrelation", "Density of states (DOS)"],
                            "per_atom": ["VP total face area", "VP total volume", "VP sphericity coefficient", 
                                        "Mean magn moment", "Mean abs magn moment", "Number of spin flips",
                                        "Topological indices"],
                            "hist_evol" : ["Voronoi face area",],
                            "hist" : ["Coordination numbers",],
                            "evol" : [ "CNs time evolution"]}
        
        self.PropChoice = wx.Choice(self, -1, choices = self.propChoices["function"])
        
        self.CorrXChoice = wx.Choice(self, -1, choices=self.propChoices["per_atom"])
        self.CorrYChoice = wx.Choice(self, -1, choices=self.propChoices["per_atom"])
        
        self.PropChoiceBtn = wx.Button(self, -1, "Plot property")
        self.CorrelateBtn = wx.Button(self, -1, "Plot correlations")
        self.AnimateBtn = wx.Button(self, -1, "Animations")
        self.CreateStatusBar()
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.propTypeChange, self.PropType)
        self.Bind(wx.EVT_RADIOBOX, self.TypeChange, self.TypeRBox)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChange, self.CalcTree)
        self.Bind(wx.EVT_BUTTON, self.DownBtnPress, self.DownBtn)
        self.Bind(wx.EVT_BUTTON, self.UpBtnPress, self.UpBtn)
        self.Bind(wx.EVT_BUTTON, self.GetDataBtnPress, self.GetData)
        self.Bind(wx.EVT_BUTTON, self.enqueuePress, self.btnEnqueue)
        self.Bind(wx.EVT_BUTTON, self.PlotProperty, self.PropChoiceBtn)
        self.Bind(wx.EVT_BUTTON, self.Correlate, self.CorrelateBtn)
        self.Bind(wx.EVT_BUTTON, self.Animate, self.AnimateBtn)
        # end wxGlade
        # initialize the tree
        self.buildTree(self.root,self.TypeRBox.GetItemLabel(self.TypeRBox.GetSelection()))
        # initialize CalcList
        self.CalcList.InsertColumn(0,'Directory', width = 180)
        self.CalcList.InsertColumn(1,'Type', width = 70)
        self.CalcList.InsertColumn(2,'NSteps', width = 100)
    
    def __set_properties(self):
        # begin wxGlade: RootFrame.__set_properties
        self.SetTitle("Siesta help scripts GUI")
        self.SetSize((820, 430))
        self.TypeRBox.SetSelection(1)
        self.PropChoice.SetSelection(4)
        self.btnEnqueue.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: RootFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        LeftSizer = wx.BoxSizer(wx.VERTICAL)
        
        PropSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        CorrSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)

        
        BtnSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer = wx.BoxSizer(wx.VERTICAL)
        RightSizer.Add(self.CalcTree, 1, wx.EXPAND, 0)
        RightSizer.Add(self.TypeRBox, 0, wx.EXPAND, 0)
        sizer_1.Add(RightSizer, 1, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.DownBtn, 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.UpBtn, 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(wx.StaticLine(self, wx.HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.GetData, 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.btnEnqueue, 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(wx.StaticLine(self, wx.HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        BtnSizer.Add(self.AnimateBtn, 0, wx.ALL|wx.EXPAND, 5)

        sizer_1.Add(BtnSizer, 0, wx.EXPAND, 0)
        LeftSizer.Add(self.CalcList, 2, wx.ALL|wx.EXPAND, 5)
        
        sizer_2.Add(self.PropType, 0, wx.ALL|wx.EXPAND, 0)
        sizer_2.Add(self.PropChoice, 0, wx.ALL|wx.EXPAND, 0)
        PropSizer.Add(sizer_2, 0, wx.ALL|wx.EXPAND, 2)
        PropSizer.Add(self.PropChoiceBtn, 1, wx.ALL|wx.EXPAND, 2)
        sizer_3.Add(self.CorrXChoice, 1, wx.ALL|wx.EXPAND, 0)
        sizer_3.Add(self.CorrYChoice, 1, wx.ALL|wx.EXPAND, 0)
        CorrSizer.Add(sizer_3, 1, wx.ALL|wx.EXPAND, 2)
        CorrSizer.Add(self.CorrelateBtn, 0, wx.ALL|wx.EXPAND, 2)

        LeftSizer.Add(PropSizer, 0, wx.ALL|wx.EXPAND, 2)
        LeftSizer.Add(CorrSizer, 0, wx.ALL|wx.EXPAND, 2)

        sizer_1.Add(LeftSizer, 1, wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()
        # end wxGlade
        
    def buildTree(self,root,ctype):
        '''Add a new root element and then its children'''        
        self.CalcTree.DeleteAllItems()
        r = len(root.split(os.sep))
        ids = {root : self.CalcTree.AddRoot(root)}
        for (dirpath, dirnames, filenames) in os.walk(root):
            if interface.isCalcOfType(ctype, dn = dirnames, fn = filenames):
                # find the number of steps in MDE file, quickly
                nsteps = interface.GetNumMDESteps(dirpath)
                ancdirs = dirpath.split('/')[r:]
                if nsteps is not None:
                    ancdirs[-1] += ' [%i]' % (nsteps)
                ad = root
                for ancdir in ancdirs:
                    d = os.path.join(ad, ancdir)
                    if not ids.has_key(d):
                        ids[d] = self.CalcTree.AppendItem(ids[ad], ancdir)
                    self.CalcTree.SortChildren(ids[ad])
                    ad = d
    
    def getSelectionDir(self):
        item =  self.CalcTree.GetSelection()
        parent = self.CalcTree.GetItemParent(item)
        path = [self.CalcTree.GetItemText(item)]
        while self.CalcTree.GetItemText(parent) != '':
            path.append(self.CalcTree.GetItemText(parent))
            parent = self.CalcTree.GetItemParent(parent)
# calculation directory
        cdir = os.sep.join(path[::-1]).split()[0]
        return cdir
    
    def OnSelChange(self, event): # wxGlade: RootFrame.<event_handler>
# calculation type        
        ctype = self.TypeRBox.GetItemLabel(self.TypeRBox.GetSelection())
# calculation directory
        cdir = self.getSelectionDir() 
        if interface.isCalcOfType(ctype, dir = cdir):
            self.btnEnqueue.Enable()
        else:
            self.btnEnqueue.Enable(False)

    def propTypeChange(self, event):
        # property type
        ptype = self.PropType.GetSelection()
        choice = {0: ["function",],
                  1: ["hist", "hist_evol", "per_atom"],
                  2: ["evol", "hist_evol", "per_atom"]}
        props = [p for pc in choice[ptype] for p in self.propChoices[pc]]
        self.PropChoice.SetItems(props)
        self.PropChoice.SetSelection(0)
         

    def TypeChange(self, event): # wxGlade: RootFrame.<event_handler>
        ctype = self.TypeRBox.GetItemLabel(self.TypeRBox.GetSelection())
        self.buildTree(self.root, ctype)

    def UpBtnPress(self, event): # wxGlade: RootFrame.<event_handler>
        # selection indices
        sind = getListCtrlSelection(self.CalcList)
        if sind:
            # number of deleted strings
            ds = 0
            for si in sind:
                self.calcs.pop(si - ds)
                self.CalcList.DeleteItem(si - ds)
                ds += 1
            return 0
        return 1

    def DownBtnPress(self, event): # wxGlade: RootFrame.<event_handler>
        # current list count
        clc = self.CalcList.GetItemCount()
# calculation type        
        ctype = self.TypeRBox.GetItemLabel(self.TypeRBox.GetSelection())
# calculation directory
        cdir = self.getSelectionDir()
        if not interface.isCalcOfType(ctype, dir = cdir):
            mbox.NoResults(cdir, ctype)
            return 1
# init steps range
        r = None
        if ctype in ('.output', '.ANI'):            
# enter dialog
            dlg = SD.StepsDialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                r = dlg.GetRange()
            dlg.Destroy()
        self.calcs.append(interface.getcalc(cdir, ctype, r))
        self.CalcList.InsertStringItem(clc, cdir[len(self.root)+1:])
        self.CalcList.SetStringItem(clc, 1, ctype)
        self.CalcList.SetStringItem(clc, 2, str(len(r)) if r is not None else '')
        return 0

    def GetDataBtnPress(self, event): # wxGlade: RootFrame.<event_handler>
        print "Event handler `GetDataBtnPress' not implemented!"
        event.Skip()

    def enqueuePress(self, event): # wxGlade: RootFrame.<event_handler>
        from sshutils import getMount, getDevice, getRemoteDir
        # on which device are we?
        cdir = self.getSelectionDir()
        mpath = getMount(cdir)
        devname, devtype = getDevice(mpath)
        if 'ssh' in devtype:
            user, hostdir = devname.split('@')
            hostname, remotempath = hostdir.split(':')
            remotedir = getRemoteDir(cdir, mpath, remotempath)
            self.enqueueRemote(remotedir, hostname, user)
        else:
            self.enqueueLocal(cdir)

    def enqueueLocal(self, cdir):
        '''Enqueue a task on a local filesystem
        Input:
         -> cdir: calculation directory on a local filesystem 
        '''
        import distutils.spawn
        # find which queue system is implemented on cluster (qstat - PBS, sinfo - SLURM)
        if distutils.spawn.find_executable('qstat') is not None:
            q = 'pbs'
        elif distutils.spawn.find_executable('sinfo') is not None:
            q = 'slurm'
        else:
            mbox.JobSubmit(None, ())
            return -1
        comm = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', q, q + '.sh'))

        submit = subprocess.Popen(['/bin/bash', comm, '-d=' + cdir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mbox.JobSubmit(q, submit.communicate())

    def enqueueRemote(self, cdir, host, user):
        '''Enqueue a task on a remote filesystem
        Input:
         -> cdir: calculation directory on a remote filesystem 
         -> host: host where to enqueue a task
         -> user: user of a remote system who enqueues a task  
        '''
        from sshutils import getSSHClient, getQueue, copyFile, removeFile, runCommand
        ssh = getSSHClient(host, user)
        # find which queue system is implemented on cluster (qstat - PBS, sinfo - SLURM)
        q = getQueue(ssh)
        if q is None:
            mbox.JobSubmit(None, ())
            return None
        # queue putter on a local machine
        localdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', q))
        putter = q + '.sh'
        
        sftp = copyFile(ssh, putter, localdir, cdir)
        remotefile = os.path.join(cdir, putter)
        stdout, stderr = runCommand(ssh, 'bash ' + remotefile + ' -d=' + cdir)
        mbox.JobSubmit(q, ('\n'.join(stdout.readlines()), '\n'.join(stderr.readlines())))
        removeFile(sftp, remotefile)
        ssh.close()
    
    def PlotProperty(self, event): # wxGlade: RootFrame.<event_handler>
# plot options - get all the data to plot
        ptype = self.PropType.GetSelection()
        pchoice = self.PropChoice.GetSelection()
        leg = [self.CalcList.GetItemText(i) for i in getListCtrlSelection(self.CalcList)]
        t1 = time.clock()
        data, info = interface.get_data(ptype, pchoice, [self.calcs[i] for i in getListCtrlSelection(self.CalcList)])        
        self.SetStatusText('Calculation time: %7.2f s.' % (time.clock() - t1))
        msg = [pchoice, leg, data, info]
        try:
            self.pf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.pf = PF.PlotFuncFrame(self)
            self.pf.Show()
        Publisher().sendMessage(('data.plot'), msg)

    def Correlate(self, event):
# correlate options - get all the data to plot
        xchoice = self.CorrXChoice.GetSelection()
        ychoice = self.CorrYChoice.GetSelection()
        leg = [self.CalcList.GetItemText(i) for i in getListCtrlSelection(self.CalcList)]
        t1 = time.clock()
        data, info = interface.get_corr(xchoice, ychoice, [self.calcs[i] for i in getListCtrlSelection(self.CalcList)])
        msg = [leg, data, info]
        try:
            self.cf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.cf = PF.PlotCorrFrame(self)
            self.cf.Show()
        Publisher().sendMessage(('corr.plot'), msg)
        

        pass
        
    def Animate(self, event):
        pass

# end of class RootFrame


