from fabric.api import settings,env
import os
import imp # Helper functions for import
import sys


# Load the parent fabfile
fabfile_bootstrap_path = os.path.dirname(os.path.dirname(__file__))
fabfile_bootstrap_parent_path = os.path.dirname(fabfile_bootstrap_path)
sys.path = [fabfile_bootstrap_path] + sys.path
fab_file, fab_path, fab_description = imp.find_module('fabfile')
fb = imp.load_module('fb',fab_file,fab_path,fab_description)

# TODO load the variables held in the fab_settings file instead of repeating here
LOCAL_PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = os.path.split(LOCAL_PROJECT_DIRECTORY)[1]

    
REMOTE_USER_DIRECTORY = '/path/to/user/home' #e.g. '/home/ubuntu/website', '/var/www/website/
REMOTE_PROJECT_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,'sites',PROJECT_NAME)
REMOTE_REPOSITORY_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,"git_repository")

REMOTE_DATABASE_BACKUP_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY, 'database_backups')

VIRTUALENV_NAME = PROJECT_NAME

env.key_filename = '~/.ssh/keyfile'

env.roledefs = {
    'application servers': ['user@server'], #i.e. ubuntu@127.0.0.1
    'database servers':[],
    'load balancers':[],
}

VIRTUALENV = PROJECT_NAME

try:
    import django
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings'% PROJECT_NAME
    from django.conf import settings as django_settings
    database_name = django_settings.DATABASES['default']['NAME']
    DJANGO_APPS = []
except:
    pass

# Test variables #

TEST_DJANGO_PROJECT_LOCATION = os.path.join(os.path.dirname(__file__), 'test_project')
    
# End variables definition #
# Start custom fabric function definition #

def test_setup_vagrant():
    # Install vagrant?
    local('vagrant box add lucid32 http://files.vagrantup.com/lucid32.box')
    
    
def test_vagrant_up(box=None):
    if not box:
        local('vagrant up lucid32')
    

def test_build_django_project():
    
    fb._python_install_python_environment()
    
## Leave this at the bottom ##
# Inject local variables into fabfile_bootstrap.fabfile module namespace #
for name in dir():
    if not name.startswith('__'):
        value = eval(name)
        setattr(fb, name, value)
from fb import *
