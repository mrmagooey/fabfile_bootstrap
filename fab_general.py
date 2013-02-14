from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd, task
import os
import platform
import subprocess
import re
from functools import wraps
from fabric.operations import _prefix_commands, _prefix_env_vars, _AttributeString
from fabric.state import output, win32
import fabric.utils 
from fabric.colors import yellow, green, blue, red

templates = {
    "nginx": {
        "local_path": "deploy/nginx.conf",
        "remote_path": "/etc/nginx/sites-enabled/%(proj_name)s.conf",
        "reload_command": "service nginx restart",
    },
    "supervisor": {
        "local_path": "%(path_to_bootstrap)s/deploy/supervisor.conf",
        "remote_path": "/etc/supervisor/conf.d/%(proj_name)s.conf",
        "reload_command": "supervisorctl reload",
    },
    "cron": {
        "local_path": "deploy/crontab",
        "remote_path": "/etc/cron.d/%(proj_name)s",
        "owner": "root",
        "mode": "600",
    },
    "gunicorn": {
        "local_path": "deploy/gunicorn.conf.py",
        "remote_path": "%(proj_path)s/gunicorn.conf.py",
    },
    "settings": {
        "local_path": "deploy/live_settings.py",
        "remote_path": "%(proj_path)s/local_settings.py",
    },
}
env.path_to_bootstrap = os.path.dirname(__file__)

def get_templates():
    """
    Returns each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected


def _print(output):
    """
    From Mezzanine
    """
    print
    print output
    print


def print_command(command):
    """
    From Mezzanine
    """
    _print(blue("$ ", bold=True) +
           yellow(command, bold=True) +
           red(" ->", bold=True))

def log_call(func):
    """
    From Mezzanine
    """
    @wraps(func)
    def logged(*args, **kawrgs):
        header = "-" * len(func.__name__)
        _print(green("\n".join([header, func.__name__, header]), bold=True))
        return func(*args, **kawrgs)
    return logged


@task
def general_apt(packages):
    """
    Installs one or more system packages via apt.
    From Mezzanine
    """
    return sudo("apt-get install -y -q " + packages)

    
@task
@log_call
def general_install():
    """
    Installs the base system and Python requirements for the entire server.
    From Mezzanine
    """
    locale = "LC_ALL=%s" % env.locale
    with hide("stdout"):
        if locale not in sudo("cat /etc/default/locale"):
            sudo("update-locale %s" % locale)
            run("exit")
    sudo("apt-get update -y -q")
    general_apt("nginx libjpeg-dev python-dev python-setuptools git-core "
        "postgresql libpq-dev memcached supervisor emacs graphviz tmux")
    sudo('apt-get upgrade -y -q')
    sudo("easy_install pip")
    sudo("pip install virtualenv mercurial")


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
        fabric.utils.error(message=msg, stdout=out, stderr=err)
    out.succeeded = not out.failed
    # If we were capturing, this will be a string; otherwise it will be None.
    return out

def _general_shell_name(run_local=True):
    if run_local:
        shell_path = local("echo $SHELL", capture=True)
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

def general_is_running(process):
    "Checks ps output for process name"
    with hide('output'):
        s = run("ps auwx")
    for x in s.split('\n'):
        if re.search(process, x):
            print "%s running"%process
            return True
    return False



