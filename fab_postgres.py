import pexpect
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

def _postgres_local_setup_pg_hba():
    """
    Update local postgres security file to allow local tcp/ip connections using md5 passwords
    """
    # TODO Find the postgres pg_hba directory
    # TODO Add in "local all all md5"
    # TODO Restart postgres
    pass

    
def _postgres_local_create_user(user, password):
    child = pexpect.spawn('createuser -d -R -S -P %s'%user)
    child.setecho(False)
    child.expect('Enter password for new role:')
    child.sendline(password)

    child.expect('Enter it again:')
    # TODO work why this needs to be here twice
    child.sendline(password)
    child.sendline(password)

def _postgres_local_create_database(db_name, db_owner):
    local('createdb -O %s %s'%(db_owner, db_name))
    
def _postgres_local_drop_user(user):
    local('dropuser %s'%user)
    
def _postgres_local_drop_db(db):
    local('dropdb %s'%db)

def postgres_local_setup():
    if LOCAL_DATABASE_USER == '':
        raise Exception("No Database user specified in fabfile")
    if LOCAL_DATABASE_NAME == '':
        raise Exception("No Database name specified in fabfile")
    if LOCAL_DATABASE_PASSWORD == '':
        raise Exception("No Database password specified in fabfile")
    _postgres_local_create_user(LOCAL_DATABASE_USER, LOCAL_DATABASE_PASSWORD)
    _postgres_local_create_database(LOCAL_DATABASE_NAME,LOCAL_DATABASE_USER)


@roles('db')
def postgres_local_db_backup():
    "Creates a local database dump of the project database, returns filename of backup"
    filename = os.path.join(os.path.dirname(__file__),
                            'local_postgresdumps/%s_%s.postgdump'%(PROJECT_NAME,time_now))
    local('pg_dump %s > %s'%(database_name,filename))
    return filename


    
    
# TODO fix this 
@roles('db')
def _postgres_upload_local_db():
    "Creates local pg_dump, copies to remote server."
    db_filepath = postgres_local_db_backup()
    db_filename = os.path.split(db_filepath)[1]
    if not exists(REMOTE_DATABASE_BACKUP_DIRECTORY):
        run('mkdir %s'%remote_directory)
    remote_file = os.path.join(remote_directory, db_filename)
    upload(db_filepath,remote_file)

@roles('db')
def _postgres_load_latest_dbdump_file():
    "Loads latest file in postgresdumps directory into server."
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

