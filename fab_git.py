
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

@roles('application servers')
def git_deploy():
    "Git based deployment with optional gunicorn restart"
    with settings(warn_only=True):
        local('git commit -a')
    local('git push')
    _remote_git_pull()

    
def _git_pull():
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

def _module_setup(import_list):
    for fab_module in import_list:
        m = __import__(fab_module)
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
            for attr in attrlist:
                globals()[attr] = getattr(m, attr)
    
