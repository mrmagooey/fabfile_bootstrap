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
    'application_servers': ['vagrant@127.0.0.1:4567'], 
    'database':['vagrant@127.0.0.1:4568'],
    'load_balancer':['vagrant@127.0.0.1:4569'],
    'vagrant_test':['vagrant@127.0.0.1:4570'],
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
    """
    Will run through and start the specified vms defined in the Vagrantfile.
    """
    local('vagrant up %s'%box)
    

def test_vagrant_destroy(box=''):
    local('vagrant destroy -f %s'%box)

    
@roles('vagrant_test')
def test_vagrant_test():
    """
    Download the base lucid32 box (if not done so already), up and then destroy it.
    """
    with settings(warn_only=True): # This will 'fail' if box is already downloaded
        test_vagrant_add_box('lucid32','http://files.vagrantup.com/lucid32.box')
    test_vagrant_up('vagrant_test')
    run('ls')
    test_vagrant_destroy('vagrant_test')


class VagrantTest(unittest.TestCase):
    def setUp(self):
        pass
        
    @unittest.skip('shouldn\'t need to run this, takes forever')
    def test_vagrant_yoyo(self):
        test_vagrant_up()
        test_vagrant_destroy()

class GeneralTest(unittest.TestCase):
    def setUp(self):
        local('vagrant up %s'%'application_server')

    def test_general():
        # To test each fabric function, need to have the fabric env.host variable set
        # Which would normally get set by a @roles decorator or using fab options
        env.host = env.roledefs['application servers'][0]
        general_upload('fabfile.py')
        

class DjangoTest(unittest.TestCase):
    def setUp(self):
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
