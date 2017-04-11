import optparse                                                                                                                                              
import time
import sys
import ntplib
from time import ctime
import json
import os
import requests
from numpy import std


def getLatency(host):
    url = "http://{0}/delay".format(host)
    client = ntplib.NTPClient()
    local_before = client.request('europe.pool.ntp.org', version=3)
    start_time = time.time()
    remote = requests.get(url)
    end_time = time.time()
    request_duration = end_time - start_time
    local = dict()
    local['offset'] = local_before.offset
    local['human_readable'] = ctime(local_before.tx_time)
    local['time'] = local_before.tx_time
    local['delay'] = local_before.delay
    local['region'] = 'europe'

    r = json.loads(remote.text)
    l = json.loads(json.dumps(local))

    # when the request started should be A
    a = local_before.tx_time
    # when the request hit the server, minus delay, is when the server *sent* the request to NTP
    b = r['time'] - r['delay']
    # local time + request duration is when the server is done responding, completing the trip
    c = l['time'] + request_duration
    # client to server delay = ctsd
    ctsd = b - a
    # server to client delay = stcd
    stcd = c - b
    latency1 = dict()
    latency1['ctsd'] = ctsd
    latency1['stcd'] = stcd
    latency1['total'] = stcd + ctsd
    return latency1


""" main method """


def main():

    global options, args
    if(len(args) == 0):
        print("boomerang_client.py takes 1 argument - host for the server component")
        print("ex: python boomerang_client ec2-13-55-16-116.ap-southeast.compute.aws.com:8000")
    elif(len(args) == 1):
        hostname = args[0]
        latency = getLatency(hostname)
        print "client to server delay: {0}".format(latency['ctsd'])
        print "server back to client delay: {0}".format(latency['stcd'])
        print "total delay: {0}".format(latency['total'])
    else:
        hostname = args[0]
        number = int(args[1])
        runs = list()
        for i in range(0, number):
            latency = getLatency(hostname)
            time.sleep(0.25)
            runs.append(latency)

        total = 0.0
        totals = list()
        for i in range(0,number):
            total += runs[i]['total']
            totals.append(runs[i]['total'])
            print runs[i]

        print "average latency {0} std deviation: {1}".format(total/number, std(totals))
        
        
    


if __name__ == '__main__':
    try:
        start_time = time.time()
        parser = optparse.OptionParser(
                formatter=optparse.TitledHelpFormatter(),
                usage=globals()['__doc__'],
                version='$Id: py.tpl 332 2008-10-21 22:24:52Z root $')

        parser.add_option ('-v', '--verbose', action='store_true',default=False, help='verbose output')
        (options, args) = parser.parse_args()
        #if len(args) < 1:
        #    parser.error ('missing argument')
        if options.verbose: print time.asctime()
        exit_code = main()
        if exit_code is None:
            exit_code = 0
        if options.verbose: print time.asctime()
        if options.verbose: print 'TOTAL TIME IN MINUTES:',
        if options.verbose: print (time.time() - start_time) / 60.0
        sys.exit(exit_code)
    except KeyboardInterrupt, e: # Ctrl-C
        raise e
    except SystemExit, e: # sys.exit()
        raise e
    except Exception, e:
        print 'ERROR, UNEXPECTED EXCEPTION'
        print str(e)
        #traceback.print_exc()
        os._exit(1)
