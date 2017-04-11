#!/usr/bin/env python

import requests
import json
import socket

class Logger:
    def __init__(self, host1="logging.secret.equipment", logNumber=999999):
        self.hostname = host1
        myhostname = socket.gethostname()
        self.application = None

        if myhostname.find('4') > -1:
            self.application = 'cars'
            self.projectId = 1
        elif myhostname.find('3') > -1 or myhostname.find('7') > -1:
            self.application = 'maintenance'
            self.projectId = 2
        elif myhostname.find('1') > -1 or myhostname.find('6') > -1:
            self.application = 'robotics'
            self.projectId = 3

        if self.application is None:
            self.projectId = logNumber

    def log(self, tag, blob=None, machine=None):
        data = dict()
        data['project_id'] = self.projectId
        data['tag'] = tag
        if type(blob) == dict:
            for k in blob.keys():
               data[k] = blob[k]

        if self.application is not None:
            data['application'] = self.application

        if blob is not None:
            data['blob'] = blob
        requestURL = "http://{0}/add".format(self.hostname)
        headers = dict()
        if machine is not None:
            headers['machine-id'] = machine
        r = requests.post(requestURL, headers=headers, data=data)
        if r.status_code == 200:
            temp = json.loads(r.text)
            return temp['success']
        else:
            return False

    def setDetails(self, name=None, description=None):
        data = dict()
        data['project_id'] = self.projectId
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        requestURL = "http://{0}/projects".format(self.hostname)
        r = requests.post(requestURL, data=data)
        temp = json.loads(r.text)
        return temp['success']

if __name__ == "__main__":
    print("hello")
    l = Logger('logging.secret.equipment', 1) 
    l.setDetails("cars", "DT Application Cars Installation")
    l.log('initialized')
    l1 = Logger('logging.secret.equipment', 2) 
    l1.setDetails("maintenance", "DT Application Maintenance Installation")
    l1.log('initialized')
    l2 = Logger('logging.secret.equipment', 3) 
    l2.setDetails("robotics", "DT Application Robotics Installation")
    l2.log('initialized')
    l2 = Logger('logging.secret.equipment', 999999) 
    l2.setDetails("default", "Unaddressed logs go here")
    l2.log('initialized')

