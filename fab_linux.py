# 2012.08.18 16:52:14 EST
from fabric.contrib.files import exists
from fabric.api import local, run, env, put, cd, sudo, settings, prefix, hosts, roles, get, hide, lcd
import os

def _latest_file_in_directory(path):
    """Returns absolute path to most recent file in directory"""
    with cd(path):
        file = run("ls -tl | awk 'NR==2{ print $NF }'")
        path = run('pwd')
        file_path = os.path.join(path, file)
        return file_path



def _check_or_create_directory(path, use_sudo = False):
    if not exists(path):
        print 'not exists %s' % path
        if use_sudo:
            sudo('mkdir %s' % path)
    else:
        run('mkdir %s' % path)



def _is_running(process):
    """Checks ps output for process name"""
    with hide('output'):
        s = run('ps auwx')
    for x in s.split('\n'):
        if re.search(process, x):
            print '%s running' % process
            return True

    return False



def something():
    pass



+++ okay decompyling /Users/peterdavis/Programming/python/fabfile_bootstrap/fab_linux.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2012.08.18 16:52:14 EST
