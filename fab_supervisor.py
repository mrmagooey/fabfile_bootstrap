
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd


def supervisor_supervisorctl(arg):
    "Run a supervisorctl command"
    if arg:
        run("supervisorctl %s"%arg)
    else:
        print "This command needs a supervisorctl argument."


def _module_setup(import_list):
    for fab_module in import_list:
        m = __import__(fab_module)
        try:
            attrlist = m.__all__
        except AttributeError:
            attrlist = dir(m)
            for attr in attrlist:
                globals()[attr] = getattr(m, attr)

