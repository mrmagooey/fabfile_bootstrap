from fabric.api import settings,env
import os
import imp # Helper functions for import
import sys
import unittest
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

# Load the parent fabfile
fabfile_bootstrap_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fabfile_bootstrap_file = os.path.join(fabfile_bootstrap_path,'fabfile.py')
fabfile_bootstrap_parent_path = os.path.dirname(fabfile_bootstrap_path)
fb = imp.load_source('fb',fabfile_bootstrap_file)
from fb import *

# TODO load the variables held in the fab_settings file instead of repeating here
LOCAL_PROJECT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = os.path.split(LOCAL_PROJECT_DIRECTORY)[1]
REMOTE_USER_DIRECTORY = '/path/to/user/home' #e.g. '/home/ubuntu/website'
REMOTE_PROJECT_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,'sites',PROJECT_NAME)
REMOTE_REPOSITORY_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY,"git_repository")
REMOTE_DATABASE_BACKUP_DIRECTORY = os.path.join(REMOTE_USER_DIRECTORY, 'database_backups')
VIRTUALENV_NAME = PROJECT_NAME

#env.key_filename = '~/.ssh/keyfile'
env.password = 'vagrant'

# Any changes here need to be mirrored in the Vagrantfile
env.roledefs = {
    'application_server': ['vagrant@127.0.0.1:4567'], 
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
TEST_LOCAL_DIRECTORY = os.path.dirname(__file__)
TEST_APPLICATIONS_DIRECTORY = os.path.join(TEST_LOCAL_DIRECTORY, 'test_applications')
TEST_DJANGO_PROJECT_LOCATION = os.path.join(TEST_APPLICATIONS_DIRECTORY, 'test_django_project')

# End variables definition #
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

def test_test():
    local('pwd')
    os.chdir(os.path.join(LOCAL_PROJECT_DIRECTORY,'../'))
    local('pwd')
    
def test_create_django_application():
    # create a django application in the test_applications directory
    # git init
    # Need to run the fabfile functions as if they were in the submodule
    
    if local('mkdir %s'%TEST_APPLICATIONS_DIRECTORY).failed:
        print 'directory already exists'
#    local('mkdir %s'%TEST_DJANGO_PROJECT_LOCATION)
    with lcd(TEST_APPLICATIONS_DIRECTORY):
        local('./django-admin.py')
    
    
# Inject local variables into fabfile_bootstrap.fabfile module namespace #
for name in dir():
    if not name.startswith('__'):
        value = eval(name)
        setattr(fb, name, value)

    
class VagrantTest(unittest.TestCase):
    def setUp(self):
        pass
        
    @unittest.skip('shouldn\'t need to run this, takes forever')
    def test_vagrant_yoyo(self):
        test_vagrant_up()
        test_vagrant_destroy()


class GeneralTest(unittest.TestCase):
    def setUp(self):
        test_vagrant_up('application_server')


    def tearDown(self):
        test_vagrant_destroy('application_server')


    def test_general(self):
        # To test each fabric function, need to have the fabric env.host variable set
        # Which would normally get set by a @roles decorator or using fab options
        env.host_string = env.roledefs['application_server'][0]
        general_upload('fabfile.py') # upload this file to the server


class DjangoTest(unittest.TestCase):
    """
    
    """
    
    def setUp(self):
        test_vagrant_up('application_server')

        
    def tearDown(self):
        test_vagrant_destroy('application_server')
        
        
    def test_django_remote_collect_static():
        pass
        
        
