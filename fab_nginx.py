from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
    prefix,hosts,roles,get,hide,lcd, task
import sys
from contextlib import contextmanager
import fab_general

__all__ = ['install']

@task
@roles('database')
def install():
    fab_general.apt_install("nginx")
    fab_general.upload_template_and_reload("nginx")
    

