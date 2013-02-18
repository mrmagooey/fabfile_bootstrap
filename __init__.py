import fab_general
import fab_python
import fab_mysql
import fab_git
import fab_postgres
import fab_supervisor
import fab_django
import fab_nginx
from contextlib import contextmanager
from fabric.api import env
import os

def fabfile_bootstrap_init(conf):
    # Users, passwords and keys
    env.remote_user = conf.get("SSH_USER", 'ubuntu')
    env.admin_pass = conf.get("ADMIN_PASS", None)
    env.password = conf.get("SSH_PASS", None)
    env.key_filename = conf.get("SSH_KEY_PATH", None)

    # Various paths
    env.local_project_root = conf.get("LOCAL_PROJECT_ROOT", None)
    env.proj_name = conf.get("PROJECT_NAME", 'project')
    env.django_name = conf.get("DJANGO_APPLICATION_NAME", env.proj_name)
    env.venv_home = conf.get("VIRTUALENV_HOME", "/home/%s/.virtualenvs" % env.remote_user)
    env.venv_path = "%s/%s" % (env.venv_home, env.django_name)
    env.remote_git_repository_path = conf.get("GIT_REPOSITORIES_PATH"+env.proj_name,
                                              "/home/%s/git/%s" % (env.remote_user,env.proj_name))
    env.webapps_path = conf.get('WEBAPPS_PATH', "/home/%s/webapps")%env.remote_user
    env.proj_path =  conf.get("PROJECT_PATH", os.path.join(env.webapps_path, env.proj_name))
    env.repo_url = conf.get("REPO_URL", None)
    
    # Django specific
    env.django_path = conf.get("DJANGO_PROJECT_PATH", env.proj_path)
    env.public_webserver_directory = conf.get("PUBLIC_WEBSERVER_DIRECTORY", # TODO decouple from django
                                              os.path.join(env.django_path, 'public'))
    env.django_static_dir = conf.get("DJANGO_STATICFILES_DIR",
                                     os.path.join(env.public_webserver_directory, 'static'))
    env.django_static_url = conf.get("DJANGO_STATIC_URL",'/public/static/')
    env.django_media_dir = conf.get("DJANGO_MEDIAFILES_DIR",
                                     os.path.join(env.public_webserver_directory, 'media'))
    env.django_media_url = conf.get("DJANGO_MEDIA_URL", '/public/media/')
    env.live_hostname = conf.get("LIVE_HOSTNAME", 'www.example.com')
    env.reqs_path = conf.get("REQUIREMENTS_PATH", None)
    
    # Database
    env.db_type = conf.get("DB_TYPE", 'sqlite3')
    env.db_pass = conf.get("DB_PASS", None)
    env.database_host = conf.get("DATABASE_SERVER", '')
    env.database_port = conf.get("DATABASE_PORT", '')

    # Gunicorn, git
    env.gunicorn_port = conf.get("GUNICORN_PORT", 8000)
    env.locale = conf.get("LOCALE", "en_US.UTF-8")
    env.deploy_key = conf.get("DEPLOY_KEY", None)
    env.git_branch = conf.get("GIT_BRANCH", 'master')

    env.roledefs = {
        'application_servers': conf.get('APPLICATION_SERVERS', []),
        'database':conf.get('DATABASE_SERVER', []),
        'load_balancer':conf.get('LOAD_BALANCING_SERVER', []),
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


