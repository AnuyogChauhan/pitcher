#!/usr/bin/env python

import os
import json
from fabric.api import env
from fabric.api import run
from fabric.api import local
from fabric.contrib.files import exists
from fabric.context_managers import cd
from fabric.operations import put
from fabric.operations import get
from fabric.operations import sudo

def initMachine():
  sudo("apt-get update")
  sudo("apt-get -y upgrade")
  sudo("apt-get install -y python-pip")
  sudo("pip install --upgrade pip")
  sudo("pip install ntplib requests flask")
  put("boomerang_server.py","/home/ubuntu/")
