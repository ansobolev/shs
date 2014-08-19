#!/usr/bin/env python
# -*- coding : utf8 -*-

''' A module interacting with PBS job queue
    (c) Inelastica package
'''
import os, string


def MakePBS(PBStemplate, PBSout, PBSsubs, submitJob, type = 'MD'):
    if PBStemplate == None:
        types = {'TS':'RUN.TS.pbs',
                 'OS':'RUN.OS.pbs',
                 'PY':'RUN.py.pbs',
                 'MD':'RUN.MD.pbs',
                 'CG':'RUN.CG.pbs'}
        PBStemplate = types[type]
        if os.path.exists( os.path.expanduser('~/.Inelastica/'+PBStemplate)):
            PBStemplate = os.path.expanduser('~/.Inelastica/'+PBStemplate)
        else:
            InelasticaDir, crap = os.path.split(__file__)
            PBStemplate = os.path.abspath(InelasticaDir+'/PBS/'+PBStemplate)

    if os.path.exists(PBStemplate):
        WritePBS(PBStemplate,PBSout,PBSsubs)
        if submitJob:
            print PBStemplate
            workingFolder, PBSfile = os.path.split(os.path.abspath(PBSout))
            SubmitPBS(workingFolder,PBSfile)
    else:
        print "ERROR: Could not find PBS template file", PBStemplate

def WritePBS(PBStemplate,PBSout,PBSsubs):
    print 'SiestaIO.WritePBS: Reading',PBStemplate
    print 'SiestaIO.WritePBS: Writing',PBSout

    # Make default job name
    fullPath, crap = os.path.split(os.path.abspath(PBSout))
    last3dir = string.split(fullPath,'/')[-3:]
    if not PBSsubs: PBSsubs = []
    newPBSsub = PBSsubs+[['$DEFJOBNAME$',last3dir[0]+'-'+last3dir[1]+'-'+last3dir[2]],['$SL$',last3dir[0]]]
    infile = open(PBStemplate)
    outfile = open(PBSout,'w')
    for line in infile:
        for sub in newPBSsub:
            line = line.replace(str(sub[0]),str(sub[1]))
        outfile.write(line)
    infile.close()
    outfile.close()

def SubmitPBS(workingfolder, pbsfile):
    cwd = os.getcwd()
    os.chdir(workingfolder)
    os.system('qsub ' + pbsfile)
    os.chdir(cwd)
    print '   ...and submitted!!!'
