import os
from fabric.contrib.files import exists
from fabric.api import local, run, env, put, cd, sudo, settings,\
     prefix, hosts, roles, get, hide, lcd

@roles('application_server')
def git_deploy(commit=False):
    "Git based deployment"
    # TODO Run tests
    if commit==True:
        local('git commit -a')
    local('git push')
    git_remote_pull()

@roles('application_server')
def _git_is_installed(run_local=False):
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
    
@roles('application_server')    
def git_setup_remote():
    """
    Set up remote git repository and install urls into local config as origin
    Sets up remote bare git repository in:
    ~/.../<REMOTE_PROJECT_BARE_GIT_DIRECTORY>/
    """

    if not _git_is_installed():
        raise Exception("git isn't installed")
        
    # Check for bare git repo parent directory
    if not exists(REMOTE_GIT_REPOSITORIES_DIRECTORY):
        run("mkdir %s"%REMOTE_GIT_REPOSITORIES_DIRECTORY)

    # Check for existence of git repo directory
    if exists(REMOTE_BARE_GIT_DIRECTORY):
        with cd(REMOTE_BARE_GIT_DIRECTORY):
            # Check if git repo directory is in fact a bare git repo
            if 'bare' not in run('cat config | grep bare'):
                print """The git repository directory exists but is not a *bare* git repository.
                
                You should ssh in, check what it is and possibly do any ssh setup manually,
                changing your REMOTE_GIT_REPOSITORIES_DIRECTORY
                and REMOTE_PROJECT_BARE_GIT_DIRECTORY to reflect any changes made."""
            else:
                print "git repository already exists at %s"%REMOTE_BARE_GIT_DIRECTORY 
    else: # bare git directory doesn't exist, safe to create from scratch
        run('mkdir %s'%REMOTE_BARE_GIT_DIRECTORY)
        with cd(REMOTE_BARE_GIT_DIRECTORY):
            run("git init --bare")

    # Add urls to local git remotes
    git_local_add_remote_urls()
    
    # Push local to new bare remote
    git_push()

    # Create working tree version in project folder
    REMOTE_PROJECT_PARENT_DIRECTORY = os.path.dirname(REMOTE_PROJECT_DIRECTORY)
    # Check if project directory exists
    if not exists(REMOTE_PROJECT_PARENT_DIRECTORY):
        run("mkdir --parents %s"%REMOTE_PROJECT_PARENT_DIRECTORY)

    with cd(REMOTE_PROJECT_PARENT_DIRECTORY):
        run('git clone %s %s'%(REMOTE_BARE_GIT_DIRECTORY,PROJECT_NAME))


@roles('application_server')
def git_push(local_repository='master'):
    with lcd(LOCAL_PROJECT_DIRECTORY):
        local("git push origin %s"%local_repository)

            
@roles('application_server')
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
    with cd(REMOTE_PROJECT_DIRECTORY):
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

def _git_local_add_submodule(submodule_directory):
    if not _git_is_installed(run_local=True):
        raise Exception("git is not installed locally")

    #TODO
    raise Exception("not yet implemented")
        
    
