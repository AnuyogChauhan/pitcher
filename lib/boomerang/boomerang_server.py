import optparse                                                                                                                                              
import time
import sys
import ntplib
from flask import Flask
from time import ctime
import json
import os

""" main method """

def main ():

    global options, args

    client = ntplib.NTPClient()
    app = Flask(__name__)
    
    @app.route("/delay")
    def delay():
        d = dict()
        #response = client.request('north-america.pool.ntp.org',version=3)
        response = client.request('europe.pool.ntp.org',version=3)
        d['offset'] = response.offset
        d['delay'] = response.delay
        d['time'] = response.tx_time
        d['region'] = 'europe'
        d['human_readable'] = ctime(response.tx_time)
        
        return json.dumps(d)

    if __name__ == "__main__":
        app.run(host='0.0.0.0',port=8000)


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
