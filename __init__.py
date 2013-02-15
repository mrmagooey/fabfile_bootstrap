from fab_general import *
from fab_python import *
from fab_mysql import *
from fab_git import *
from fab_postgres import *
from fab_supervisor import *
from fab_django import *
from contextlib import contextmanager

def fabfile_bootstrap_init(conf):
    env.remote_user = conf.get("SSH_USER", 'ubuntu')
    env.db_pass = conf.get("DB_PASS", None)
    env.admin_pass = conf.get("ADMIN_PASS", None)
    env.password = conf.get("SSH_PASS", None)
    env.key_filename = conf.get("SSH_KEY_PATH", None)
    
    env.proj_name = conf.get("PROJECT_NAME", 'project')
    env.django_name = conf.get("DJANGO_APPLICATION_NAME", env.proj_name)
    
    env.venv_home = conf.get("VIRTUALENV_HOME", "/home/%s/.virtualenvs" % env.remote_user)
    env.venv_path = "%s/%s" % (env.venv_home, env.django_name)
    
    env.remote_git_repository_path = conf.get("GIT_REPOSITORIES_PATH"+env.proj_name,
                                              "/home/%s/git/%s" % (env.remote_user,env.proj_name))
    
    env.webapps_path = conf.get('WEBAPPS_PATH', "/home/%s/webapps")%env.remote_user
    env.proj_path =  conf.get("PROJECT_PATH", os.path.join(env.webapps_path, env.proj_name))
    
    env.django_path = os.path.join(env.proj_path, env.django_name)
    
    env.public_webserver_directory = conf.get("PUBLIC_WEBSERVER_DIRECTORY",
                                              os.path.join(env.django_path, 'public'))
    env.django_static_dir = conf.get("DJANGO_STATICFILES_DIR", 
                                     os.path.join(env.public_webserver_directory, 'static'))
    env.django_static_url = conf.get("DJANGO_STATIC_URL", 
                                     '/public/static/')
    env.django_media_dir = conf.get("DJANGO_MEDIAFILES_DIR", 
                                     os.path.join(env.public_webserver_directory, 'media'))
    env.django_media_url = conf.get("DJANGO_MEDIA_URL", 
                                     '/public/media/')
    
    env.repo_url = conf.get("REPO_URL", None)
    env.reqs_path = conf.get("REQUIREMENTS_PATH", None)
    env.gunicorn_port = conf.get("GUNICORN_PORT", 8000)
    env.locale = conf.get("LOCALE", "en_US.UTF-8")
    env.deploy_key = conf.get("DEPLOY_KEY", None)
    env.db_type = conf.get("DB_TYPE", 'sqlite3')
    env.git_branch = conf.get("GIT_BRANCH", 'master')
    
    env.live_hostname = conf.get("LIVE_HOSTNAME", 'www.example.com')
    
    env.roledefs = {
        'application_servers': conf.get('APPLICATION_SERVERS', []),
        'database':conf.get('DATABASE_SERVERS', []),
        'load_balancer':conf.get('LOAD_BALANCING_SERVERS', []),
    }
    
    env.path_to_bootstrap = os.path.dirname(__file__)
    
    
@contextmanager
def project():
    """
    Runs commands within the project's directory.
    """
    with python_virtualenv():
        with cd(env.proj_path):
            run('git checkout django_backend')
        with cd(env.django_path):
            yield
    
    
