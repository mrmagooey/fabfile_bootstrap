__author__ = 'mrmagooey'
import os
import datetime
import re
import subprocess
import sys
from fabric.contrib.files import exists
from fabric.api import local,run,env,put,cd,sudo,settings,\
     prefix,hosts,roles,get,hide,lcd

# Put this directory at the start of the PYTHONPATH
sys.path = [os.path.dirname(__file__)] + sys.path

todays_date = datetime.date.today().strftime('%y%m%d')
time_now = datetime.datetime.now().strftime("%y%m%d-%H%M")

from fab_general import *
from fab_python import *
from fab_mysql import *
from fab_git import *
from fab_postgres import *
from fab_supervisor import *

