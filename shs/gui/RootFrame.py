# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import wx
import ConfigParser
from wx.lib.mixins.listctrl import getListCtrlSelection
from wx.lib.pubsub import pub

from gui.RootGUI import RootGUI
from StepsDialog import StepsDialog
from PlotFrame import PlotFuncFrame, PlotCorrFrame
import interface
import mbox


class RootFrame(RootGUI):

    calcs = []
    plot_frame = None

    def __init__(self, *args, **kwds):
        super(RootFrame, self).__init__(*args, **kwds)
        # set root
        self.root = self.set_root()

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
        self.build_tree(self.root, self.typeRBox.GetItemLabel(self.typeRBox.GetSelection()))
        # initialize calc list
        self.calcList.InsertColumn(0, 'Directory', width=180)
        self.calcList.InsertColumn(1, 'Type', width=70)
        self.calcList.InsertColumn(2, 'NSteps', width=100)

    def set_root(self):
        """
        Sets root directory fr GUI based on config file
        :return: Root directory
        """
        config_dir = os.path.expanduser("~/.local/shs")
        config_file = os.path.join(config_dir, "shs_gui.cfg")
        # check the file and create one if it's not there
        if not os.path.isfile(config_file):
            os.makedirs(config_dir)
            open(config_file, 'w').close()
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        # if config exists and has needed option
        if config.has_option("general", "root_dir"):
            return config.get("general", "root_dir")
        # make config
        if not config.has_section("general"):
            config.add_section("general")
        dlg = wx.DirDialog(self, "Select root directory")
        if dlg.ShowModal() == wx.ID_OK:
            root_dir = dlg.GetPath()
            config.set("general", "root_dir", root_dir)
        else:
            sys.exit(1)
        with open(config_file, 'w') as f:
            config.write(f)
        return root_dir

    def build_tree(self, root, calc_type):
        """
        Adds a new root element and then its children
        :param root: root directory for the tree
        :param calc_type: calculation type
        """
        self.calcTree.DeleteAllItems()
        r = len(root.split(os.sep))
        ids = {root: self.calcTree.AddRoot(root)}
        for (dir_path, dir_names, file_names) in os.walk(root):
            if interface.isCalcOfType(calc_type, dn=dir_names, fn=file_names):
                # find the number of steps in MDE file, quickly
                nsteps = interface.GetNumMDESteps(dir_path)
                ancdirs = dir_path.split(os.sep)[r:]
                if nsteps is not None:
                    ancdirs[-1] += ' [%i]' % nsteps
                ad = root
                for ancdir in ancdirs:
                    d = os.path.join(ad, ancdir)
                    if not d in ids:
                        ids[d] = self.calcTree.AppendItem(ids[ad], ancdir)
                    self.calcTree.SortChildren(ids[ad])
                    ad = d
    
    def get_selection_dir(self):
        item = self.calcTree.GetSelection()
        parent = self.calcTree.GetItemParent(item)
        path = [self.calcTree.GetItemText(item)]
        while parent.IsOk():
            path.append(self.calcTree.GetItemText(parent))
            parent = self.calcTree.GetItemParent(parent)
# calculation directory
        calc_dir = os.sep.join(path[::-1]).split()[0]
        return calc_dir
        # return os.sep.join((self.root, calc_dir))
    
    def onSelChange(self, event):
# calculation type        
        ctype = self.typeRBox.GetItemLabel(self.typeRBox.GetSelection())
# calculation directory
        cdir = self.get_selection_dir() 
        if interface.isCalcOfType(ctype, dir=cdir):
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
        self.build_tree(self.root, ctype)

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
        cdir = self.get_selection_dir()
        if not interface.isCalcOfType(ctype, dir=cdir):
            mbox.NoResults(cdir, ctype)
            return 1
# init steps range
        r = None
        if ctype in ('.output', '.ANI'):            
# enter dialog
            dlg = StepsDialog(None)
            if dlg.ShowModal() == wx.ID_OK:
                r = dlg.GetRange()
            dlg.Destroy()
        self.calcs.append(interface.getCalc(cdir, ctype, r))
        self.calcList.InsertStringItem(clc, cdir[len(self.root)+1:])
        self.calcList.SetStringItem(clc, 1, ctype)
        self.calcList.SetStringItem(clc, 2, str(len(r)) if r is not None else '')
        return 0

    def on_enqueue_press(self, _):
        from sshutils import getMount, getDevice, getRemoteDir
        # on which device are we?
        calc_dir = self.get_selection_dir()
        mount_path = getMount(calc_dir)
        device_name, device_type = getDevice(mount_path)
        if 'ssh' in device_type:
            user, host_dir = device_name.split('@')
            hostname, remote_mount_path = host_dir.split(':')
            remote_dir = getRemoteDir(calc_dir, mount_path, remote_mount_path)
            self.enqueue_remote(remote_dir, hostname, user)
        else:
            self.enqueue_local(calc_dir)

    @staticmethod
    def enqueue_local(calc_dir):
        """
        Enqueue a task on a local filesystem
        :param calc_dir: calculation directory on a local filesystem
        :return: error_code (0 is OK)
        """
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

        submit = subprocess.Popen(['/bin/bash', comm, '-d=' + calc_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mbox.JobSubmit(q, submit.communicate())

    @staticmethod
    def enqueue_remote(calc_dir, host, user):
        """
        Enqueue a task on a remote filesystem
        :param calc_dir: calculation directory on a remote filesystem
        :param host: host where to enqueue a task
        :param user: user of a remote system who enqueues a task
        :return: error code (0 is OK)
        """
        from sshutils import getSSHClient, getQueue, copyFile, removeFile, runCommand
        ssh = getSSHClient(host, user)
        # find which queue system is implemented on cluster (qstat - PBS, sinfo - SLURM)
        q = getQueue(ssh)
        if q is None:
            mbox.JobSubmit(None, ())
            return None
        # queue putter on a local machine
        local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', q))
        putter = q + '.sh'
        
        sftp = copyFile(ssh, putter, local_dir, calc_dir)
        remote_file = os.path.join(calc_dir, putter)
        stdout, stderr = runCommand(ssh, 'bash ' + remote_file + ' -d=' + calc_dir)
        mbox.JobSubmit(q, ('\n'.join(stdout.readlines()), '\n'.join(stderr.readlines())))
        removeFile(sftp, remote_file)
        ssh.close()
    
    def plotBtnPress(self, event):
        if self.noteBook.GetSelection() == 0:
            self.plot_property()
        else:
            self.plot_correlation()
    
    def plot_property(self):
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
            self.plot_frame.Raise()
        except (AttributeError, wx.PyDeadObjectError):
            self.plot_frame = PlotFuncFrame(self)
            self.plot_frame.Show()
        pub.sendMessage('data.plot', message=msg)

    def plot_correlation(self):
        # correlate options - get all the data to plot
        xchoice = self.xCorr.GetSelection()
        ychoice = self.yCorr.GetSelection()
        leg = [self.calcList.GetItemText(i) for i in getListCtrlSelection(self.calcList)]
        data, info = interface.getCorr(xchoice, ychoice, [self.calcs[i] for i in getListCtrlSelection(self.calcList)])
        msg = [leg, data, info]
        try:
            self.plot_frame.Raise()
        except (AttributeError, wx.PyDeadObjectError):
            self.plot_frame = PlotCorrFrame(self)
            self.plot_frame.Show()
        pub.sendMessage('corr.plot', message=msg)
