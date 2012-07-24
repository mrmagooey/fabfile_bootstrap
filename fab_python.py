
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd
from fabfile import *
import sys


def _python_setup_virtualenvwrapper(run_local=True):
    if local:
        if not _python_check_for_python_library('virtualenvwrapper'):
            local('pip install virtualenvwrapper')
    else:
        # TODO
        pass

def _python_virtualenv_path(run_local=True):
    pass
        
def _python_install_python_environment(run_local=True):
    """
    Install some minimum elements of the python ecosystem.
    """
    if local:
        try:
            import pip
        except ImportError:
            if os_name != "Windows":
                with settings(warn_only=True):
                    if local("easy_install pip").failed:
                        print "In order to install pip superuser privileges will be needed."
                        with settings(warn_only=False):                    
                            local("sudo easy_install pip")
            else:
                print "pip not installed"

        try:
            import virtualenvwrapper
        except ImportError:
            if os_name != "Windows":
                with settings(warn_only=True):
                    if local("pip install virtualenvwrapper").failed:
                        print "In order to install virtualenvwrapper superuser privileges will be needed."
                        with settings(warn_only=False):
                            local("sudo pip install virtualenvwrapper")
            else:
                print "virtualenvwrapper not installed"

        # Check that virtualenvwrapper.sh has been correctly installed        
        with settings(warn_only=True):
            if _blocal("workon").failed == True: # using blocal so that .profile gets loaded
                # TODO find where virtualenvwrapper installed virtualenvwrapper.sh to 
                local("echo \"source /usr/local/bin/virtualenvwrapper.sh\" >> ~/.profile")

                
def _python_check_interpreter_version(local=True):
    if local:
        return sys.version
    else:
        # TODO
        pass


def _local_python_dependencies():
    # Will return the dependencies of whatever virtualenv is active when fab is called
    return local("pip freeze",capture=True).split('\n')

    
def _python_check_for_python_library(library):
    if library in _local_python_dependencies():
        return True
    else:
        return False

    
def mirror_python_setup(use_git=False):
    "Mirrors the local python libraries to the server"
    # Decide whether or not to push a requirements.txt file to server
    if not use_git:
        python_deps = ' '.join(_local_python_dependencies())
        with prefix("workon %s"%cpython_virtualenv):
            run("pip install %s"%python_deps)
    else:
        local('pip freeze > requirements.txt')
        with settings(warn_only=True):
            local("git add requirements.txt")
            local("git commit -m 'fab requirements.txt commit' requirements.txt")
            local('git push %s'%env['roles'])
            _remote_git_pull()
            with prefix("workon %s"%cpython_virtualenv):
                with cd(REMOTE_PROJECT_DIRECTORY):
                    run("pip install -r requirements.txt")


def python_test():
    print general_test()


def _module_setup(import_list):
    for fab_module in import_list:
        m = __import__(fab_module)
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
            for attr in attrlist:
                globals()[attr] = getattr(m, attr)
