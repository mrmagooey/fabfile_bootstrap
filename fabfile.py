__author__ = 'mrmagooey'
import os
import datetime
import re
import subprocess

from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

import sys
sys.path.append(os.path.dirname(__file__))

todays_date = datetime.date.today().strftime('%y%m%d')
time_now = datetime.datetime.now().strftime("%y%m%d-%H%M")

# Change this to reflect what fabric commands you want to use
import_list = [
    'fab_general',
    'fab_python',
    'fab_git',
    'fab_postgres',
    'fab_supervisor',
]

for fab_module in import_list:
    m = __import__(fab_module)
    m._module_setup(import_list) # cross-links each fab module
    try:
        attrlist = m.__all__
    except AttributeError:
        attrlist = dir(m)
        for attr in attrlist:
            globals()[attr] = getattr(m, attr)





    

