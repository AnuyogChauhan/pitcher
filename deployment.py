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

#env.hosts = ['slow.secret.equipment','fast.secret.equipment']
#env.user = 'ubuntu'

def deployDocker():
    run("rm -rf ~/car-network")
    run("mkdir -p ~/car-network")
    put("Dockerfile.traditional", "~/car-network/")
    put("Makefile", "~/car-network/")
    put("lib", "~/car-network/")
    put("Car*", "~/car-network/")
    put("carcalc.py", "~/car-network/")
    with cd("~/car-network"):
        sudo("make build")
    put("conf/carnetwork.systemd", "~/")
    sudo("chmod 644 ~/carnetwork.systemd")
    sudo("mv ~/carnetwork.systemd /etc/systemd/system/carnetwork.service")
    sudo("systemctl daemon-reload")
    sudo("systemctl start --no-block carnetwork")
    sudo("systemctl enable carnetwork")




