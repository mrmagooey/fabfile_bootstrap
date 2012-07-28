import pexpect
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

def postgres_local_drop_user(user):
    local('dropuser %s'%user)


def postgres_local_drop_user(user):
    local('dropuser %s'%user)

    
def postgres_local_create_user(user,password):
    child = pexpect.spawn('createuser -D -R -S -P %s'%user)
    child.expect('Enter password for new role: ')
    child.sendline(password)
    child.expect('Enter it again: ')
    child.sendline(password)

    
def postgres_local_create_database(db_owner, database_name):
    local('createdb -O %s %s'%(db_owner, database_name))


def postgres_local_setup_project_database(project_name):
    postgres_local_create_user(project_name,password)
    postgres_local_create_database(project_name)


@roles('db')
def postgres_db_backup():
    "Creates a local database dump of the project database using -O flag"
    filename = os.path.join(os.path.dirname(__file__),'postgresdumps/%screatedb.postgdump'%time_now)
    local('pg_dump -O %s > %s'%(database_name,filename))
    return filename

    
@roles('db')
def postgres_upload_local_db():
    "Creates local pg_dump, copies to remote server."
    db_filepath = db_backup()
    db_filename = os.path.split(db_filepath)[1]
    remote_directory = '/home/ubuntu/postgresdumps'
    if not exists(remote_directory):
        run('mkdir %s'%remote_directory)
    remote_file = os.path.join(remote_directory, db_filename)
    upload(db_filepath,remote_file)

@roles('db')
def _postgres_load_latest_dbdump_file():
    "Doesn't work - Loads latest file in postgresdumps directory into server."
    file = _latest_file_in_directory('postgresdumps')
    sudo('psql < %s'%file,user='postgres')

@roles('db')
def _postres_generate_remote_pg_dump():
    filename = '/home/ubuntu/postgresbackups/%screatedb.postgdump'%time_now
    with settings(warn_only=True):
        run("mkdir postgresbackups")
    sudo("pg_dump -O --clean %s > %s"%(database_name,filename),user="postgres")

@roles('db')
def _postgres_download_remote_pg_dump():
    file_path = latest_file_in_directory("/home/ubuntu/postgresbackups")
    file = os.path.split(file_path)[-1]
    with settings(warn_only=True):
        local("mkdir remote_db_backups")
    get(file_path,"remote_db_backups")

@roles('db')
def postgres_download_remote_pg_backup():
    "Generate pg_dump of remote pg db and download to local machine"
    _generate_remote_pg_dump()
    _download_remote_pg_dump()

def _module_setup(import_list):
    for fab_module in import_list:
        m = __import__(fab_module)
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
            for attr in attrlist:
                globals()[attr] = getattr(m, attr)
