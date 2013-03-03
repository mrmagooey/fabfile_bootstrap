import os
from fabric.contrib.files import exists, upload_template, append
from fabric.api import local, run, env, put, cd, sudo, settings,\
     prefix, hosts, roles, get, hide, lcd
from fab_general import task, log_call

@task
@roles('application_servers')
def git_push_pull():
    "Git based deployment"
    local('git push')
    git_remote_pull()


@roles('application_servers')
def git_is_installed(run_local=False):
    if run_local:
        if run("git --version 2>&1 >/dev/null && echo $?") == '0':
            print 'git is installed on the local server\n'
            return True
        else:
            return False
    else:
        if run("git --version 2>&1 >/dev/null && echo $?") == '0':
            print 'git is installed on remote server\n'
            return True
        else:
            return False

@roles('application_servers')
def git_setup_remote():
    """
    Set up remote git repository and install urls into local config as origin
    Sets up remote bare git repository in:
    ~/.../<REMOTE_PROJECT_BARE_GIT_DIRECTORY>/
    """
    if not git_is_installed():
        raise Exception("git isn't installed")
    # Check for bare git repo parent directory
    run('mkdir -p %s'%env.remote_git_repository_path)
    # Check for existence of git repo directory
    with cd(env.remote_git_repository_path):
        run("git init --bare", )
    # Add urls to local git remotes
    git_local_add_remote_urls()
    # Push local to new bare remote
    local('git push')
    # Create working tree version in project folder
    remote_parent_directory = os.path.dirname(env.proj_path)
    # Check if project directory exists
    run("mkdir -p %s"%remote_parent_directory)
    with cd(remote_parent_directory):
        run('git clone %s %s'%(env.remote_git_repository_path, env.project_name))

@task
@log_call
@roles('application_servers')
def clone_git_repository():
    if exists(env.proj_path):
        return 
    if env.deploy_key:
        deploy_key_local_path = os.path.join(env.local_project_root, env.deploy_key)
        upload_template(deploy_key_local_path, '~/.ssh/')
        run("chmod 600 ~/.ssh/%s"% env.deploy_key)
        # Add key to .ssh/config
        # TODO make this more robust
        try: 
            repo_url = env.repo_url.split('@')[1]
        except IndexError:
            repo_url = env.repo_url
        hostname = repo_url.split(':')[0] 
        repository_name = env.repo_url.split(':')[1]
        ssh_config_string = """
Host git_repo
    Hostname %s
    User git
    IdentityFile ~/.ssh/%s
        """ % (hostname, env.deploy_key)
        append('~/.ssh/config', ssh_config_string)
        # TODO answer yes 
        run("git clone ssh://git_repo/%s %s" % (repository_name, env.proj_path))
    else:
        run("git clone %s %s" % (env.repo_url, env.proj_path))
        

@roles('application_servers')
def git_local_add_remote_urls():
    "Add the remote git repo addresses to the local git config"
    _GIT_URL_SPEC_PATH = env.host_string+":"+\
                         REMOTE_BARE_GIT_DIRECTORY.replace(REMOTE_USER_DIRECTORY,'')
    with lcd(LOCAL_PROJECT_DIRECTORY):
        # Check if 'origin' exists
        if 'origin' not in local("git remote -v", capture=True):
            local("git remote add origin %s"%_GIT_URL_SPEC_PATH)
        else:
            # check current host url against [origin] in .git/config
            if _GIT_URL_SPEC_PATH not in local("git remote -v",capture=True):
                local("git remote set-url --add origin %s"%_GIT_URL_SPEC_PATH)


def git_remote_pull():
    with cd(env.proj_path):
        run("git pull")


def git_fix_divergent_remote_git_repository():
    "Useful to fix 'Your branch and origin/master have diverged'"
    run('git reset --hard origin/master')


def git_fix_non_branched_remote_git_repository():
    "Useful to fix 'Not currently on any branch'"
    run('git stash && git checkout master')


def _git_server_name_is_git_remote():
    names = env['roles']
    git_remote_names =  local('git remote',capture=True).split("\n")
    for n in names:
        if n not in git_remote_names:
            return False
    return True


