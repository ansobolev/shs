# -*- coding: utf-8 -*-

import os, time, subprocess
import wx
from wx.lib.mixins.listctrl import getListCtrlSelection
from wx.lib.pubsub import Publisher 

from gui.RootGUI import RootGUI
import StepsDialog as SD, PlotFrame as PF, CorrDialog as CD
import interface
import mbox

class RootFrame(RootGUI):

    if os.path.exists('/home/physics/calc'):
        root = '/home/physics/calc'
    else:
        root = '/home/andrey/calc'

    calcs = []

    def __init__(self, *args, **kwds):
        super(RootFrame, self).__init__(*args, **kwds)
        # initialize choices
        self.propChoices = interface.dataClasses()
        calc_data_types = self.propChoices.types()
        calc_data_classes = self.propChoices.classes(calc_data_types[0])
        corr_classes = self.propChoices.classes("Histogram")
        self.propType.SetItems(calc_data_types)
        self.propChoice.SetItems(calc_data_classes)
        self.xCorr.SetItems(corr_classes)
        self.yCorr.SetItems(corr_classes)
        self.propType.SetSelection(0)
        self.propChoice.SetSelection(0)
        self.xCorr.SetSelection(0)
        self.yCorr.SetSelection(0)
        # initialize calc tree
        self.buildTree(self.root,self.typeRBox.GetItemLabel(self.typeRBox.GetSelection()))
        # initialize calc list
        self.calcList.InsertColumn(0,'Directory', width = 180)
        self.calcList.InsertColumn(1,'Type', width = 70)
        self.calcList.InsertColumn(2,'NSteps', width = 100)

    def buildTree(self,root,ctype):
        '''Add a new root element and then its children'''        
        self.calcTree.DeleteAllItems()
        r = len(root.split(os.sep))
        ids = {root : self.calcTree.AddRoot(root)}
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
                        ids[d] = self.calcTree.AppendItem(ids[ad], ancdir)
                    self.calcTree.SortChildren(ids[ad])
                    ad = d
    
    def getSelectionDir(self):
        item =  self.calcTree.GetSelection()
        parent = self.calcTree.GetItemParent(item)
        path = [self.calcTree.GetItemText(item)]
        while self.calcTree.GetItemText(parent) != '':
            path.append(self.calcTree.GetItemText(parent))
            parent = self.calcTree.GetItemParent(parent)
# calculation directory
        cdir = os.sep.join(path[::-1]).split()[0]
        return cdir
    
    def onSelChange(self, event):
# calculation type        
        ctype = self.typeRBox.GetItemLabel(self.typeRBox.GetSelection())
# calculation directory
        cdir = self.getSelectionDir() 
        if interface.isCalcOfType(ctype, dir = cdir):
            self.enqueueBtn.Enable()
        else:
            self.enqueueBtn.Enable(False)

    def propTypeChange(self, event):
        # property type
        pt_num = self.propType.GetSelection()
        pt = self.propType.GetItems()[pt_num]
        self.propChoice.SetItems(self.propChoices.classes(pt))
        self.propChoice.SetSelection(0)

    def typeChange(self, event): 
        ctype = self.typeRBox.GetItemLabel(self.typeRBox.GetSelection())
        self.buildTree(self.root, ctype)

    def upBtnPress(self, event):
        # selection indices
        sind = getListCtrlSelection(self.calcList)
        if sind:
            # number of deleted strings
            ds = 0
            for si in sind:
                self.calcs.pop(si - ds)
                self.calcList.DeleteItem(si - ds)
                ds += 1
            return 0
        return 1

    def downBtnPress(self, event):
        # current list count
        clc = self.calcList.GetItemCount()
# calculation type        
        ctype = self.typeRBox.GetItemLabel(self.typeRBox.GetSelection())
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
        self.calcs.append(interface.getCalc(cdir, ctype, r))
        self.calcList.InsertStringItem(clc, cdir[len(self.root)+1:])
        self.calcList.SetStringItem(clc, 1, ctype)
        self.calcList.SetStringItem(clc, 2, str(len(r)) if r is not None else '')
        return 0

    def enqueuePress(self, event):
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
    
    def plotBtnPress(self, event):
        if self.noteBook.GetSelection() == 0:
            self.plotProperty()
        else:
            self.plotCorrelation()
    
    def plotProperty(self):
        # plot options - get all the data to plot
        ptype = self.propType.GetItems()[self.propType.GetSelection()]
        pchoice = self.propChoice.GetItems()[self.propChoice.GetSelection()]
        data_class = self.propChoices.dataClass(ptype, pchoice)
        leg = [self.calcList.GetItemText(i) for i in getListCtrlSelection(self.calcList)]
        t1 = time.clock()
        plot_data = interface.getData(ptype, data_class, leg, 
                                       [self.calcs[i] for i in getListCtrlSelection(self.calcList)])        
        self.SetStatusText('Calculation time: %7.2f s.' % (time.clock() - t1))
        msg = plot_data
        try:
            self.pf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.pf = PF.PlotFuncFrame(self)
            self.pf.Show()
        Publisher().sendMessage(('data.plot'), msg)

    def plotCorrelation(self):
        # correlate options - get all the data to plot
        xchoice = self.xCorr.GetSelection()
        ychoice = self.yCorr.GetSelection()
        leg = [self.calcList.GetItemText(i) for i in getListCtrlSelection(self.calcList)]
        t1 = time.clock()
        data, info = interface.get_corr(xchoice, ychoice, [self.calcs[i] for i in getListCtrlSelection(self.calcList)])
        msg = [leg, data, info]
        try:
            self.cf.Raise()
        except (AttributeError, wx._core.PyDeadObjectError):
            self.cf = PF.PlotCorrFrame(self)
            self.cf.Show()
        Publisher().sendMessage(('corr.plot'), msg)
