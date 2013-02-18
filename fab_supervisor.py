from fabric.contrib.files import exists, upload_template
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd, task
import fab_general

__all__ = ['install', 'add_to_supervisord_conf',
           'supervisor_restart','supervisor_supervisorctl']

@task
@roles('application_servers')
def install():
    import fab_python
    if check_supervisor_alive():
        return True
    fab_python.python_check_and_install_easy_install()
    sudo("easy_install supervisor")
    sudo("supervisorctl status")

@task
@roles('application_servers')
def add_to_supervisord_conf():
    template = fab_general.get_templates()['supervisor']
    upload_template(template['local_path'], template['remote_path'], env, use_sudo=True)
    sudo("supervisord", warn_only=True)
    sudo("supervisorctl status")

@task    
@roles('application_servers')
def supervisor_restart(app=None):
    if not app:
        sudo("supervisorctl restart")
    else:
        sudo("supervisorctl restart %s"%app)
        
def supervisor_reload():
    sudo("supervisorctl reload")
    
def check_supervisor_alive():
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


