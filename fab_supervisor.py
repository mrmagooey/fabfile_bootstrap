from fabric.contrib.files import exists, upload_template
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd, task
from fab_python import python_check_and_install_easy_install
from fab_general import get_templates
# Currently this assumes that supervisor is going to be installed
# in the base system python installation, and root access is
# available

@task
@roles('application_servers')
def supervisor_setup():
    # Check if it's already up
    if supervisor_check_supervisor_alive():
        return True

    # Check if easy_install is installed, install if necessary
    python_check_and_install_easy_install()
    sudo("easy_install supervisor")
    template = get_templates()['supervisor']
    upload_template(template['local_path'], template['remote_path'], env, use_sudo=True)
    sudo("supervisord", warn_only=True)
    sudo("supervisorctl status")

    
def supervisor_add_to_supervisord_conf():
    pass

    
def supervisor_restart(app=None):
    if not app:
        sudo("supervisorctl restart")
    else:
        sudo("supervisorctl restart %s"%app)

        
def supervisor_reload():
    sudo("supervisorctl reload")

    
def supervisor_check_supervisor_alive():
    supervisor_ctl_return = run("supervisorctl status" , warn_only= True) 
    if supervisor_ctl_return.failed:
        print "ERROR: Supervisor is NOT up\n"
        return False
    else:
        print "Supervisor is up\n"
        return True
@task
@roles('application_servers')
def supervisor_supervisorctl(arg):
    "Run a supervisorctl command on remote server"
    if arg:
        sudo("supervisorctl %s"%arg)
    else:
        print "This command needs a supervisorctl argument."


