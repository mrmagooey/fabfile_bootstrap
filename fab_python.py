from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
    prefix,hosts,roles,get,hide,lcd, task
import sys
from contextlib import contextmanager
from fab_general import _blocal
from fab_git import git_remote_pull

@task
@roles('application_servers')
def python_mkvirtualenv(virtualenv_name=None):
    if virtualenv_name:
        run("mkvirtualenv %s"%virtualenv_name)
    else:
        run("mkvirtualenv %s"%env.proj_name)

        
@contextmanager
def python_virtualenv():
    """
    Runs commands within the project's virtualenv.
    """
    # with cd(env.venv_path):
    with prefix("source %s/bin/activate" % env.venv_path):
        yield

@task
@roles('application_servers')
def python_pip(packages):
    """
    Installs one or more Python packages within the virtual environment.
    """
    with python_virtualenv():
        return sudo("pip install %s" % packages)

@task            
@roles('application_servers')
def python_install_virtualenvwrapper():
    python_check_and_install_easy_install()
    python_check_and_install_pip()
    
    sudo('pip install virtualenvwrapper')
    run("echo \"source /usr/local/bin/virtualenvwrapper.sh\" >> ~/.bash_profile")
    
def python_check_and_install_easy_install():
    # easy_install --help should return a status code 0 if it runs
    # 2>&1 = combine error stream (2) with ordinary output
    # >/dev/null 'delete' both streams by sending to null 
    if not run("easy_install --help 2>&1 >/dev/null && echo $?") == '0':
        print "easy_install installed on target machine\n "
        #TODO add OS (e.g mac, rpm, windows) robust install method for easy_install
        # sudo("sudo yum install python-setuptools")
        sudo("sudo apt-get install python-setuptools")

def python_check_and_install_pip():
    python_check_and_install_easy_install()
    if run("pip --help 2>&1 >/dev/null && echo $?") != '0':
        run("easy_install pip")
    
                
def python_check_interpreter_version(run_local=True):
    if run_local:
        return sys.version
    else:
        # TODO
        pass


def python_dependencies(run_local=True):
    # Will return the dependencies of whatever virtualenv is active when fab is called
    if run_local:
        return local("pip freeze",capture=True).split('\n')
    else:
        with python_virtualenv():
            return run("pip freeze",capture=True).split('\n')
    
def python_check_if_package_installed(library):
    raise Exception
    if library in python_dependencies():
        return True
    else:
        return False

@task
@roles('application_servers')    
def python_mirror_virtualenv(use_git=False):
    "Mirrors the local python libraries to the server"
    if not use_git:
        deps = python_dependencies()
        for dep in deps:
            if 'pygraphviz' in dep:
                print 'pygraphviz is NOT being installed, organise graphviz yourself'
                deps.remove(dep)
        python_deps = ' '.join(deps)
        with prefix("workon %s"%env.proj_name):
            run("pip install %s"%python_deps)
    else:
        local('pip freeze > requirements.txt')
        with settings(warn_only=True):
            local("git add requirements.txt")
            local("git commit -m 'fab requirements.txt commit' requirements.txt")
            local('git push %s'%env['roles'])
            git_remote_pull()
            with prefix("workon %s"%env.proj_name):
                with cd(env.proj_path):
                    run("pip install -r requirements.txt")


def python_local_setup_virtualenvwrapper():
    "Because I can never remember this set of steps"
    # check if it is already installed
    if not python_check_if_package_installed('virtualenvwrapper'):
        local('pip install virtualenvwrapper')
        # Check what kind of shell is the default on the system
        # Add "source virtualenvwrapper.sh" to that shells startup path (*rc)
    else:
        # TODO: all the work goes here
        pass


def python_local_install_python_environment():
    """
    Install some minimum elements of the python ecosystem.
    """
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

                