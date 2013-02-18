from fabric.contrib.files import exists, upload_template
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
        "local_path": "%(path_to_bootstrap)s/deploy/nginx.conf",
        "remote_path": "/etc/nginx/sites-enabled/%(proj_name)s.conf",
        "reload_command": "service nginx restart",
    },
    "supervisor": {
        "local_path": "%(path_to_bootstrap)s/deploy/supervisor.conf",
        "remote_path": "/etc/supervisor/conf.d/%(proj_name)s.conf",
        "reload_command": "supervisorctl reload",
    },
    "cron": {
        "local_path": "%(path_to_bootstrap)s/deploy/crontab",
        "remote_path": "/etc/cron.d/%(proj_name)s",
        "owner": "root",
        "mode": "600",
    },
    "gunicorn": {
        "local_path": "%(path_to_bootstrap)s/deploy/gunicorn.conf.py",
        "remote_path": "%(proj_path)s/gunicorn.conf.py",
    },
    "django_local_settings": {
        "local_path": "%(path_to_bootstrap)s/deploy/local_settings.py",
        "remote_path": "%(django_path)s/local_settings.py",
    },
}


def get_templates():
    """
    Returns each of the templates with env vars injected.
    """
    injected = {}
    for name, data in templates.items():
        injected[name] = dict([(k, v % env) for k, v in data.items()])
    return injected

    
def upload_template_and_reload(name):
    """
    Uploads a template only if it has changed, and if so, reload a
    related service.
    """
    template = get_templates()[name]
    local_path = template["local_path"]
    remote_path = template["remote_path"]
    reload_command = template.get("reload_command")
    owner = template.get("owner")
    mode = template.get("mode")
    remote_data = ""
    if exists(remote_path):
        with hide("stdout"):
            remote_data = sudo("cat %s" % remote_path)
    with open(local_path, "r") as f:
        local_data = f.read()
        # if "%(db_pass)s" in local_data:
        #     env.db_pass = db_pass()
        local_data %= env
    clean = lambda s: s.replace("\n", "").replace("\r", "").strip()
    if clean(remote_data) == clean(local_data):
        return
    upload_template(local_path, remote_path, env, use_sudo=True, backup=False)
    if owner:
        sudo("chown %s %s" % (owner, remote_path))
    if mode:
        sudo("chmod %s %s" % (mode, remote_path))
    if reload_command:
        sudo(reload_command)


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
def apt_install(packages):
    """
    Installs one or more system packages via apt.
    From Mezzanine
    """
    return sudo("apt-get install -y -q " + packages)


@task
@log_call
@roles('application_servers')
def install_web():
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
    apt_install("libjpeg-dev python-dev python-setuptools git-core "
        "libpq-dev supervisor emacs graphviz tmux")
    sudo('apt-get upgrade -y -q')
    sudo("easy_install pip")
    sudo("pip install virtualenv mercurial")
    
    
@task
@log_call
@roles('database')
def install_database():
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
    if env.db_type == "postgresql_psycopg2":
        apt_install("postgres")
    elif env.db_type == "mysql":
        apt_install("mysql")
    elif env.db_type == 'sqlite3':
        pass
    sudo('apt-get upgrade -y -q')


@task
@log_call
@roles('database')
def install_load_balancers():
    """
    installs the base system and python requirements for the entire server.
    from mezzanine
    """
    locale = "lc_all=%s" % env.locale
    with hide("stdout"):
        if locale not in sudo("cat /etc/default/locale"):
            sudo("update-locale %s" % locale)
            run("exit")
    sudo("apt-get update -y -q")
    general_apt("nginx")
    sudo('apt-get upgrade -y -q')
    
    
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

    
def general_shell_name(run_local=True):
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
        
        
def general_latest_file_in_directory(path, run_local=True):
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
        

def general_check_or_create_directory(path,use_sudo=False):
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



