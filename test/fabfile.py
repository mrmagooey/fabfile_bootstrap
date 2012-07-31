from fabric.api import settings,env
import os
import imp # Helper functions for import
import sys
import unittest
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

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

#env.key_filename = '~/.ssh/keyfile'
env.password = 'vagrant'

# Any changes here need to be mirrored in the Vagrantfile
env.roledefs = {
    'application servers': ['vagrant@127.0.0.1:4567'], 
    'database servers':['vagrant@127.0.0.1:4568'],
    'load balancers':['vagrant@127.0.0.1:4569'],
    'vagrant test':['vagrant@127.0.0.1:4570'],
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

TEST_VM_PORT = 4568 # As defined in Vagrantfile
TEST_DJANGO_PROJECT_LOCATION = os.path.join(os.path.dirname(__file__), 'test_project')
    
# End variables definition #
# Start custom fabric function definition #

# Vagrant Tests #

def test_vagrant_list_boxes():
    pass
    
def test_vagrant_add_box(box_name, box_address):
    if box_name == None:
        raise Exception("No box_name specified for install")
    local('vagrant box add %s %s'%(box_name,box_address))

    
def test_vagrant_setup():
    test_vagrant_add_box('lucid32','http://files.vagrantup.com/lucid32.box')
    
    
def test_vagrant_up(box=''):
    local('vagrant up %s'%box)
    

def test_vagrant_destroy(box=''):
    local('vagrant destroy %s'%box)

    
@roles('vagrant test')
def test_vagrant_lucid32():
    """
    Download the base lucid32 box (if not done so already), up and then destroy it.
    """
    with settings(warn_only=True):
        test_vagrant_add_box('lucid32','http://files.vagrantup.com/lucid32.box')
    test_vagrant_up('lucid32')
    run('ls')
    test_vagrant_destroy('lucid32')


    
class VagrantEnvironmentTest(unittest.TestCase):
    def setUp(self):
        pass
    def test_vagrant_boxes_available(self):
        test_vagrant
    def test_vagrantUp(self):
        pass
    def test_vagrantUp(self):
        pass
        

    
# Django Tests #    
def test_build_django_project():
#    test_vagrant_up('lucid32')
    fb._python_install_python_environment()

    
## Leave this at the bottom ##
# Inject local variables into fabfile_bootstrap.fabfile module namespace #
for name in dir():
    if not name.startswith('__'):
        value = eval(name)
        setattr(fb, name, value)
from fb import *
