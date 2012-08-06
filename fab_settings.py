from fabric.api import settings,env
import os
import fabfile_bootstrap.fabfile as fb
import sys


LOCAL_PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = os.path.split(LOCAL_PROJECT_DIRECTORY)[1]

REMOTE_USER_DIRECTORY = '/path/to/userdir' #e.g. '/home/ubuntu/website', '/var/www/website/
REMOTE_PROJECT_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,'sites',PROJECT_NAME)
REMOTE_REPOSITORY_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,"git_repo")

REMOTE_DATABASE_BACKUP_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY, 'database_backups')

VIRTUALENV_NAME = PROJECT_NAME

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'% PROJECT_NAME
    from django.conf import settings as django_settings
    DATABASE_NAME = django_settings.DATABASES['default']['NAME']
    DJANGO_APPS = []
except:
    DATABASE_NAME = ''
    
env.key_filename = '~/.ssh/keyfile'

env.roledefs = {
    'application servers': ['user@server'], #i.e. ubuntu@127.0.0.1
    'database servers':[],
    'load balancers':[],
}

# End variable definition #
# Start custom fabric function definition #

def custom_server_setup(pypy=False):
    # Core system setup
    with settings(warn_only=True):
        if run("supervisorctl status").failed:
            sudo("easy_install supervisor")

    ## supervisord
#    put("fab_confs/supervisord.conf","/etc/", use_sudo=True)
    if not _is_running("supervisord"):
        run("supervisord")

    # Set up local git information about remote repository
    # If it doesn't already exist
    if not _server_name_is_git_remote():
        local("git remote set-url %s ssh://%s/home/ubuntu/django/%s.git"%(server_name,env.host_string,project_name))
        local("git push %s master"%server_name)
    _check_or_create_directory("/var/www",use_sudo=True)

    #install python modules
    python_deps = ' '.join(_local_python_dependencies())
    with prefix("workon %s"%cpython_virtualenv):
        run("pip install %s"%python_deps)

    #Test a few things
    run("supervisorctl status")



## Leave this at the bottom ##
# Inject local variables into fabfile_bootstrap.fabfile module namespace #


for name in dir():
    if not name.startswith('__'):
        value = eval(name)
        setattr(fb, name, value)
from fabfile_bootstrap.fabfile import *
