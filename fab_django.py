from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd


def django_remote_collect_static():
    with prefix('workon %s'%VIRTUALENV_NAME):
        run("yes yes | %s/manage.py collectstatic"%REMOTE_PROJECT_DIRECTORY)

        
def django_remote_schemamigration_all():
    for app in DJANGO_APPS:
        with prefix('workon %s'%VIRTUALENV_NAME):
            run('%s/manage.py schemamigration %s --auto'%(REMOTE_PROJECT_DIRECTORY,app))

            
def django_remote_migrate(app_name):
    "Single South migration for app_name"
    with prefix('workon %s'%VIRTUALENV_NAME):
        run('%s/manage.py migrate %s'%(REMOTE_PROJECT_DIRECTORY,app_name))

        
def django_remote_migrate_all():
    "South migrate all applications"
    with prefix('workon %s'%VIRTUALENV_NAME):
        run('%s/manage.py migrate --all'%REMOTE_PROJECT_DIRECTORY)

        
def django_schema_migration():
    with settings(warn_only=True):
        remote_schemamigration_all()
        remote_migrate_all()
