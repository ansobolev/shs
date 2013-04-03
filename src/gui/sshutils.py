'''
#
# This file is a part of Siesta Help Scripts GUI
#
# (c) Andrey Sobolev, 2013
#

Created on 03.04.2013

@author: andrey
'''

import os, paramiko

def getMount(path):
    path = os.path.realpath(os.path.abspath(path))
    while path != os.path.sep:
        if os.path.ismount(path):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    return path

def getDevice(path):
    "Get the device mounted at path"
    # uses "/proc/mounts"
    pathname = os.path.normcase(path) # might be unnecessary here
    try:
        with open("/proc/mounts", "r") as ifp:
            for line in ifp:
                fields= line.rstrip('\n').split()
                # note that line above assumes that
                # no mount points contain whitespace
                if fields[1] == pathname:
                    return fields[0], fields[2]
    except EnvironmentError:
        pass
    return None # explicit

def getSSHClient(host, user):
    'Returns paramiko ssh client'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user)
    return ssh

def runCommand(ssh, cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    return stdout, stderr
    
def findExecutable(ssh, filename):
    stdout, _ = runCommand(ssh, 'which ' + filename)
    return len(stdout.readlines()) != 0

def getQueue(ssh):
    'Returns queue system implemented on a remote cluster'
    if findExecutable(ssh, 'qstat'):
        return 'pbs'
    elif findExecutable(ssh, 'sinfo'):
        return 'slurm'
    else:
        return None

def copyFile(ssh, filename, localdir, remotedir):
    'Copies a file filename from localdir to remotedir'
    sftp = ssh.open_sftp()
    localpath = os.path.join(localdir, filename)
    remotepath = os.path.join(remotedir, filename)
    sftp.put(localpath, remotepath)
    return sftp

def removeFile(sftp, remotefile):
    'Removes a file at given remotepath'
    sftp.remove(remotefile)

def getRemoteDir(localdir, localmpath, remotempath):
    ''' Gets remote path of a directory mounted on local machine 
    Input:
     -> localdir : a directory mounted on local machine
     -> localmpath : a mountpoint of a directory on a local machine
     -> remotempath : a directory on a remote machine which is mounted at localmpath  
    '''
    return localdir.replace(localmpath, remotempath)

if __name__ == '__main__':
    host = 'tornado.susu.ac.ru'
    user = 'physics'
    ssh = getSSHClient(host, user)
    
        