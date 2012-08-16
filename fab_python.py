from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
    prefix,hosts,roles,get,hide,lcd
from fabfile import *
import sys

# Assumes that python is installed on the target system

def python_mkvirtualenv(virtualenv_name=None):
    if virtualenv_name:
        run("mkvirtualenv %s"%virtualenv_name)
    else:
        run("mkvirtualenv %s"%PROJECT_NAME)

    
def _python_check_and_install_easy_install():
    # easy_install --help should return a status code 0 if it runs
    # 2>&1 = combine error stream (2) with ordinary output
    # >/dev/null 'delete' both streams
    if not run("easy_install --help 2>&1 >/dev/null && echo $?") == '0':
        #TODO add OS (e.g mac, rpm, windows) robust install method for easy_install
        # sudo("sudo yum install python-setuptools")
        sudo("sudo apt-get install python-setuptools")

def _python_check_and_install_pip(virtualenv=None):
    _python_check_and_install_easy_install()
    if not run("pip --help 2>&1 >/dev/null && echo $?") == '0':
        run("easy_install pip")
    
def _python_local_install_python_environment():
    """
    Install some minimum elements of the python ecosystem.
    """
    _python_check_and_install_easy_install()
    try:
        import pip
    except ImportError:
        with settings(warn_only=True):
            if local("easy_install pip").failed:
                print "In order to install pip superuser privileges will be needed."
                with settings(warn_only=False):
                    local("sudo easy_install pip")
    try:
        import virtualenvwrapper
    except ImportError:
        with settings(warn_only=True):
            if local("pip install virtualenvwrapper").failed:
                print "In order to install virtualenvwrapper superuser privileges will be needed."
                with settings(warn_only=False):
                    local("sudo pip install virtualenvwrapper")
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

    
def _python_check_if_package_installed(library):
    if library in _local_python_dependencies():
        return True
    else:
        return False


@roles('application servers')    
def python_mirror_virtualenv(use_git=False):
    "Mirrors the local python libraries to the server"
    # Decide whether or not to push a requirements.txt file to server
    # Check remote virtualenv setup
    if 'ERROR' in run('workon'):
        # create new virtualenv
        pass
        if not use_git:
            python_deps = ' '.join(_local_python_dependencies())
            with prefix("workon %s"%VIRTUALENV_NAME):
                run("pip install %s"%python_deps)
        else:
            local('pip freeze > requirements.txt')
            with settings(warn_only=True):
                local("git add requirements.txt")
                local("git commit -m 'fab requirements.txt commit' requirements.txt")
                local('git push %s'%env['roles'])
                _remote_git_pull()
                with prefix("workon %s"%VIRTUALENV_NAME):
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

def _python_local_setup_virtualenvwrapper():
    "Because I can never remember this set of steps"
    # check if it is already installed
    if not _python_check_if_package_installed('virtualenvwrapper'):
        local('pip install virtualenvwrapper')
        # Check what kind of shell is the default on the system
        # Add "source virtualenvwrapper.sh" to that shells startup path (*rc)
    else:
        # TODO: all the work goes here
        pass
                