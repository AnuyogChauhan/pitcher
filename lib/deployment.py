#!/usr/bin/env python

import os
import json
from datetime import datetime
from fabric.api import env
from fabric.api import run
from fabric.api import local
from fabric.contrib.files import exists
from fabric.context_managers import cd
from fabric.operations import put
from fabric.operations import get
from fabric.operations import sudo

#env.user = 'frogsf'
#env.password = 'frogsf'

deployLocation = "/home/frogsf/mouseblaster/"

def init():
    sudo("sudo apt-get install -y liboscpack-dev")


def deploySystemdService(servicename, servicefile, startscript, deploylocation):
    sudo("systemctl stop {0} || echo \"{0} not running\"".format(servicename))
    sudo("unlink /etc/systemd/system/multi-user.target.wants/{0}.service || echo \"not linked\"".format(servicename))
    put(servicefile, "/home/frogsf/")
    put(startscript, deploylocation)
    sudo("chmod 655 /home/frogsf/*.systemd")
    sudo("mv /home/frogsf/{0}.systemd /lib/systemd/system/{0}.service".format(servicename))
    sudo("chmod 755 {0}/*".format(deploylocation))
    sudo("systemctl daemon-reload")
    sudo("systemctl start --no-block {0}".format(servicename))
    sudo("systemctl enable {0}".format(servicename))


def fiddle():
    run("cat /etc/default/apport | sed 's/enabled=1/enabled=0/g' > /tmp/apport")
    sudo("mv /tmp/apport /etc/default/apport")


def deploy():
    run("rm -rf {0}".format(deployLocation))
    run("mkdir -p {0}".format(deployLocation))
    files = ['mouseblaster/main.c', 'mouseblaster/Makefile']
    for f in files:
        put(f, deployLocation)

    with cd(deployLocation):
        run("make")

    deploySystemdService("mouseblaster", "mouseblaster/conf/mouseblaster.systemd", "mouseblaster/conf/runMouseBlaster.sh", deployLocation)


def initXenialMachine():   # ubuntu 16.04
    sudo("apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
    sudo("apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'")
    sudo("apt-get update")
    sudo("apt-get install -y docker-engine make")


def initYakketyMachine():  # ubuntu 16.10
    sudo("apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D")
    sudo("apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-yakkety main'")
    sudo("apt-get update")
    sudo("apt-get install -y docker-engine make")




