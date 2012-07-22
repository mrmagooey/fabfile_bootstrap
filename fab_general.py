from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd
import os
import platform
import subprocess

from fabric.operations import _prefix_commands, _prefix_env_vars, _AttributeString
from fabric.state import output, win32
from fabric.utils import error

def _blocal(command, capture=False):
    """
    Slightly modified version of fabrics 'local' function designed
    to make the underlying subprocess.Popen call use bash.

    Taken from fabric operations.py file.
    """
    given_command = command
    # Apply cd(), path() etc
    wrapped_command = _prefix_commands(_prefix_env_vars(command), 'local')
    if output.debug:
        print("[localhost] local: %s" % (wrapped_command))
    elif output.running:
        print("[localhost] local: " + given_command)
    # Tie in to global output controls as best we can; our capture argument
    # takes precedence over the output settings.
    dev_null = None
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
    else:
        dev_null = open(os.devnull, 'w+')
        # Non-captured, hidden streams are discarded.
        out_stream = None if output.stdout else dev_null
        err_stream = None if output.stderr else dev_null
    try:
        cmd_arg = wrapped_command if win32 else [wrapped_command]
        p = subprocess.Popen(cmd_arg, shell=True, stdout=out_stream,
            stderr=err_stream,executable="/bin/bash")
        (stdout, stderr) = p.communicate()
    finally:
        if dev_null is not None:
            dev_null.close()
    # Handle error condition (deal with stdout being None, too)
    out = _AttributeString(stdout.strip() if stdout else "")
    err = _AttributeString(stderr.strip() if stderr else "")
    out.failed = False
    out.return_code = p.returncode
    out.stderr = err
    if p.returncode != 0:
        out.failed = True
        msg = "local() encountered an error (return code %s) while executing '%s'" % (p.returncode, command)
        error(message=msg, stdout=out, stderr=err)
    out.succeeded = not out.failed
    # If we were capturing, this will be a string; otherwise it will be None.
    return out

def _general_shell_name(run_local=True):
    if run_local:
        shell_path = local("echo $SHELL",capture=True)
        if 'zsh' in shell_path:
            return 'zsh'
        if 'bash' in shell_path:
            return 'bash'
        if 'csh' in shell_path:
            return 'csh'
    else:
        # TODO
        raise Exception
        
def _general_os_name(run_local=True):
    if run_local:
        return _general_os_details(local=True)[0]
    else:
        # TODO
        pass

        
def _general_os_details(run_local=True):
    if run_local:
        return platform.uname()
    else:
        pass

        
def _general_latest_file_in_directory(path, run_local=True):
    "Returns absolute path to most recent file in directory"
    if run_local:
        # TODO properly test this
        with lcd(path):
            file = local('ls -tl | awk \'NR==2{ print $NF }\'')
            path = local('pwd')
            file_path = os.path.join(path,file)
            return file_path
    else:
        with cd(path):
            file = run('ls -tl | awk \'NR==2{ print $NF }\'')
            path = run('pwd')
            file_path = os.path.join(path,file)
            return file_path
        

def _general_check_or_create_directory(path,use_sudo=False):
    if not exists(path):
        print "not exists %s"%path
        if use_sudo:
            sudo("mkdir %s"%path)
    else:
        run("mkdir %s"%path)

def _general_is_running(process):
    "Checks ps output for process name"
    with hide('output'):
        s = run("ps auwx")
    for x in s.split('\n'):
        if re.search(process, x):
            print "%s running"%process
            return True
    return False

def general_upload(local_path,remote_path):
    "'put' wrapper, checks local_path for absolute uri" 
    if not os.path.isabs(local_path):
        local_file_path = os.path.abspath(local_path)
    else:
        local_file_path = local_path
        local_file = os.path.split(local_file_path)[1]
    put(local_path,remote_path)


def _module_setup(import_list):
    for fab_module in import_list:
        m = __import__(fab_module)
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
            for attr in attrlist:
                globals()[attr] = getattr(m, attr)
