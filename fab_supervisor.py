from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

# Currently this assumes that supervisor is going to be installed
# in the base system python installation, and root access is
# available

def supervisor_setup():
    # Check if it's already up
    if _supervisor_check_supervisor_alive():
        return True

    # Check if easy_install is installed, install if necessary
    _python_check_and_install_easy_install()
    run("easy_install supervisor")
    run("echo_supervisord_conf > supervisord.conf") # install conf to $HOME/supervisord.conf
    run("supervisord")
    run("supervisorctl status")
    
def supervisor_add_to_supervisord_conf():
    # TODO
    pass

def supervisor_restart(app=None):
    # TODO
    if not app:
        run("supervisorctl restart")
    else:
        run("supervisorctl restart %s"%app)

def supervisor_reload():
    run("supervisorctl reload")

def _supervisor_check_supervisor_alive():
    if run("supervisorctl status 2>&1 >/dev/null && echo $?") != '0':
        print "ERROR: Supervisor is NOT up\n"
        return False
    else:
        print "Supervisor is up\n"
        return True

def supervisor_supervisorctl(arg):
    "Run a supervisorctl command on remote server"
    if arg:
        run("supervisorctl %s"%arg)
    else:
        print "This command needs a supervisorctl argument."


