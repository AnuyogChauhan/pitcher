import logging
import asyncore, socket
import httplib, requests
import struct
import time
import threading
import Queue
import json
import re
import uuid

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)-8s %(message)s')

class ENSClientError(Exception):
    ## Exception thrown for ENS specific errors.
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "ENSClientError: %s" % self.reason

header = struct.Struct('>I I')


class ENSEndpoint:
    def __init__(self, endpoint):
        m = re.match(r'^(tcp|udp|http|https)://\[?([0-9]+(?:\.[0-9]+){3}|[0-9a-fA-F]{4}(?:[\:]+[0-9a-fA-F]{4}){0,7}[\:]*|[a-zA-Z0-9\-\.]+)\]?:([0-9]+)$', endpoint)
        if not m:
            raise ENSClientError("Invalid endpoint %s" % endpoint)
        self.endpoint = m.group(0)
        self.protocol = m.group(1)
        self.host = m.group(2)
        self.port = int(m.group(3))
        self.sa = [r[4] for r in socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM) if r[0] == socket.AF_INET or r[0] == socket.AF_INET6]


class ENSEventSession():
    def __init__(self, app, cloudlet, interface, binding):
        logging.info("Create ENSSession to interface %s on application %s" % (interface, app))
        self.app = app
        self.cloudlet = cloudlet
        self.interface = interface
        self.binding = binding
        self.conn = None

    def connect(self):
        # Connect to port in the interface binding.
        logging.info("Connecting to ENS interface %s at %s" % (self.interface, self.binding))
        try:
            eventEndpoint = ENSEndpoint(self.binding)
            sa = eventEndpoint.sa[0]
            logging.debug("Connecting cloudlet at %s:%d" % (sa[0], sa[1]))
            self.conn = socket.create_connection( (sa[0], sa[1]) )
            self.conn.send(header.pack(0,1))
            rsp = header.unpack(self.conn.recv(8))
        except ENSClientError:
            logging.error("Invalid endpoint %s for %s" % (self.binding, self.interface))
            return False
        except socket.error:
            logging.error("Failed to connect to endpoint %s for %s" % (self.binding, self.interface))
            return False

        return True

    def request(self, data):
        if self.conn:
            s = json.dumps(data)
            self.conn.sendall(header.pack(len(s), 0) + s)
            hdr = header.unpack(self.conn.recv(header.size))
            rsp = self.conn.recv(hdr[0])
            return json.loads(rsp);
        else:
            return None

    def event(self, data):
        if self.conn:
            self.conn.send(json.dumps(data))

    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None

    def __term__ (self):
        close(self)


class ENSHttpSession():
    def __init__(self, app, cloudlet, interface, binding):
        logging.info("Create ENSSession to interface %s on application %s" % (interface, app))
        self.app = app
        self.cloudlet = cloudlet
        self.interface = interface
        self.binding = binding
        self.conn = None

    def connect(self):
        # Connect to port in the interface binding.
        logging.info("Connecting to HTTP interface %s at %s" % (self.interface, self.binding))
        return True

    def request(self, method, api, data):
        headers = {'content-type': 'application/json','API-KEY': self.binding['access_token']}
        url = self.binding['endpoint'] + api
        if method == 'get':
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                rsp = json.loads(response.text)
                logging.info("API response: %s" %json.dumps(rsp))
                return json.dumps(rsp)
            else:
                logging.error("Service error: [%s] - %s" %(response.status_code, response.reason));

        return None

    def event(self, data):
        return

    def close(self):
        return

    def __term__ (self):
        return

class ENSNetworkSession():
    def __init__(self, app, cloudlet, interface, binding):
        logging.info("Create ENSNetworkSession to interface %s on application %s" % (interface, app))
        self.app = app
        self.cloudlet = cloudlet
        self.interface = interface
        self.binding = binding
        self.conn = None
        self.rfile = None

    def connect(self):
        # Connect to port in the interface binding.
        logging.info("Connecting to Network interface %s at %s" % (self.interface, self.binding))
        try:
            nwEndpoint = ENSEndpoint(self.binding)
            sa = nwEndpoint.sa[0]
            logging.debug("Connecting cloudlet at %s:%d" % (sa[0], sa[1]))
            self.conn = socket.create_connection( (sa[0], sa[1]) )
            self.rfile = self.conn.makefile("rb")
        except ENSClientError:
            logging.error("Invalid endpoint %s for %s" % (self.binding['endpoint'], self.interface))
            return False
        except socket.error:
            logging.error("Failed to connect to endpoint %s for %s" % (self.binding['endpoint'], self.interface))
            return False

        return True
    
    def request(self, data):
        if self.conn:
            self.conn.sendall(data)
            return self.rfile.read()
	    #return self.conn.sendall(data)
        else:
            return None

    def close(self):
        if self.rfile:
            self.rfile.close()
            self.conn.close()
            self.rfile = self.conn = None

    def __term__ (self):
        close(self)

class ENSClient():

    # Prober class probes a cloudlet by opening a connection to the cloudlet
    # WLM and repeatedly measuring the round trip time until it is manually
    # destroyed.
    class Probe(asyncore.dispatcher):
        def __init__(self, cloudlet, config, app):
            asyncore.dispatcher.__init__(self)
            logging.info("Probe cloudlet %s for application %s" % (str(cloudlet), app))
            self.app = app
            self.cloudlet = cloudlet
            self.sampling = False
            self.samples = []

            if "endpoints" in config and "probe" in config["endpoints"]:
                try:
                    probe = config["endpoints"]["probe"]
                    probeEndpoint = ENSEndpoint(probe)
                    sa = probeEndpoint.sa[0]
                    logging.debug("Probe cloudlet at %s:%d" % (sa[0], sa[1]))
                    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.connect(sa)
                except ENSClientError:
                    logging.error("Invalid probe endpoint %s for cloudlet %s" % (probe, cloudlet))
                except socket.error:
                    logging.error("Failed to connect to probe endpoint %s for cloudlet %s" % (probe, cloudlet))
                self.buffer = "ENS-PROBE %s\r\n" % self.app
            else:
                logging.error("Missing probe endpoint configuration for cloudlet %s" % cloudlet)

        def handle_connect(self):
            pass

        def handle_error(self):
            pass

        def handle_close(self):
            logging.debug("Closing probe for cloudlet %s" % self.cloudlet)
            self.close()

        def handle_read(self):
            self.end_time = time.time()
            rsp = self.recv(8192)
            logging.debug("Received (%s): %s" % (self.cloudlet, rsp))

            if not self.sampling:
                # Check that the microservice is supported
                params = rsp.splitlines()[0].split(' ')
                if params[0] == "ENS-PROBE-OK":
                    # Microservice is supported, so save microservice data
                    self.buffer = "ENS-RTT %s\r\n" % self.app
                    self.sampling = True
                else:
                    # Microservice is not supported, so just close the socket
                    # and wait for other probes to finish.
                    self.close()
            else:
                # Must be doing RTT estimation
                rtt = self.end_time - self.start_time
                logging.debug("RTT = %f" % rtt);
                self.samples.append(rtt)
                if len(self.samples) < 10:
                    self.buffer = "ENS-RTT %s\r\n" % self.app
                else:
                    logging.debug("Completed 10 RTT probes to %s" % self.cloudlet)

        def writable(self):
            return (len(self.buffer) > 0)

        def handle_write(self):
            self.start_time = time.time()
            sent = self.send(self.buffer)
            logging.debug("Sent (%s): %s" % (self.cloudlet, self.buffer))
            self.buffer = self.buffer[sent:]

        def rtt(self):
            if len(self.samples):
                return sum(self.samples) / float(len(self.samples))
            else:
                return -1

    def __init__(self, edge_domain, app):
        # Open the configuration file to get the Discovery Server URL, API key
        # and SDK version.
        self.sdkconfig = {}
        with open("mecsdk.conf") as sdkfile:
            logging.info("Loading MEC SDK settings")
            for line in sdkfile:
                name, var = line.partition("=")[::2]
                self.sdkconfig[name.strip()] = var.strip()
            if "DiscoveryURL" not in self.sdkconfig:
                raise ENSClientError("Missing DiscoveryURL in mecsdk.conf file")
            if "SdkVersion" not in self.sdkconfig:
                raise ENSClientError("Missing SdkVersion in mecsdk.conf file")
            if "ApiKey" not in self.sdkconfig:
                raise ENSClientError("Missing ApiKey in mecsdk.conf file")

        self.app = app
        self.cloudlet = ""
        self.http_bindings = {}
        self.faas_bindings = {}
        self.network_bindings = {}
        self.probed_rtt = 0.0
        #self.cloudlets = {}

    def init(self):

        """
        Requests initialization of the hosted application on the ENS platform.

        Return True or False indicating success of operation.
        """

        developer_id, app_id = self.app.split('.')

        if ("Environment" in self.sdkconfig) and (self.sdkconfig["Environment"] == "localhost"):
            # Send a service request to workload-tester to instantiate the application and microservices.
            aac = "http://127.0.0.1:8080"
            try:
                headers = {'content-type': 'application/json'}
                url = "%s/api/v1.0/workload-tester/%s/%s" %(str(aac),developer_id,app_id)
                response = requests.post(url,headers=headers)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    logging.debug("Server Response ==>" + json.dumps(data))
                else:
                    logging.error("Failed to initialize application: %s" % rsp)
                    return False

                if "http-gateway" in data["endpoints"]:
                    for http_endpoint in data["endpoints"]["http-gateway"]:       
                        self.http_bindings[http_endpoint["http-api-id"]] = http_endpoint["endpoint"]
                    logging.debug("Http Bindings ==>" + json.dumps(self.http_bindings))
                if "event-gateway" in data["endpoints"]:
                    for event_endpoint in data["endpoints"]["event-gateway"]:
                        self.faas_bindings[event_endpoint["event-id"]] = event_endpoint["endpoint"]
                    logging.debug("FaaS Bindings ==>" + json.dumps(self.faas_bindings))
                if "network-binding" in data["endpoints"]:
                   for network_endpoint in data["endpoints"]["network-binding"]:
                       self.network_bindings[network_endpoint["network-id"]] = network_endpoint["endpoint"]
                   logging.debug("Network Bindings ==>" + json.dumps(self.network_bindings))
                return True
            except socket.error:
                pass
        else:
            # Contact the Discovery Server to get a candidate list of cloudlets for the app
            # and the contact details for the app@cloud instance.
            dr = {}
            r = requests.get("%s/api/v1/discover/%s/%s?sdkversion=%s" % (self.sdkconfig["DiscoveryURL"], developer_id, app_id, self.sdkconfig["SdkVersion"]),
                             headers = {"Authorization": "Bearer %s" % self.sdkconfig["ApiKey"]})
            if r.status_code == httplib.OK:
                dr = r.json()

            logging.debug("Discovery server response:\n%s" % dr)

            if "cloudlets" not in dr:
                logging.error("No cloudlets element in Discovery Server response")
                return False

            if "cloud" not in dr or "endpoints" not in dr["cloud"] or "app@cloud" not in dr["cloud"]["endpoints"]:
                logging.error("No app@cloud element in Discovery Server response")
                return False

            cloudlets = dr["cloudlets"]
            aac = dr["cloud"]["endpoints"]["app@cloud"]

            if len(cloudlets) == 0:
                logging.error("No cloudlets to probe")
                return False

            # Create probes for each cloudlet
            logging.debug("Probe %d cloudlets" % len(cloudlets))
            probes = [ENSClient.Probe(c, v, self.app) for c,v in cloudlets.iteritems()]

            # Run the probes for one second
            start = time.time()
            while (time.time() - start) < 1:
                asyncore.loop(timeout=1, count=1, use_poll=True)

            logging.info("Probes completed");
            for probe in probes:
                probe.close()

            # Pick the probe with the shortest RTT
            rtts = [(p.rtt(), p.cloudlet) for p in probes if p.rtt() != -1]
            rtts = sorted(rtts, key=lambda p: p[0])
            logging.debug(repr(rtts))

            if len(rtts) == 0:
                return False

            self.cloudlet = rtts[0][1]
            self.probed_rtt = rtts[0][0]

            # Send a service request to platform app@cloud to instantiate the application and microservices.
            try:
                ## TODO:
                # Need to finalize how client-id will be generated. Options:
                # 1. Generate it once during first use of ENSClient and get it stored in the conf.
                # 2. Generate it every time ENSClient gets instantiated.
                #
                # As of now, taking the second approach.
                #
                client_id = str(uuid.uuid4()).replace('-', '')
                headers = {'content-type': 'application/json'}
                url = "%s/api/v1.0/app_cloud/%s/%s/%s/%s" %(str(aac),developer_id,app_id,cloudlets[self.cloudlet],client_id)
                response = requests.post(url,headers=headers)
                if response.status_code == 200:
                    data = json.loads(response.text)
                else:
                    logging.error("Failed to initialize application: %s" % rsp)
                    return False

                if "http-gateway" in data["endpoints"]:
                    for http_endpoint in data["endpoints"]["http-gateway"]:       
                        self.http_bindings[http_endpoint["http-api-id"]] = http_endpoint["endpoint"]
                    logging.debug("Http Bindings ==>" + self.http_bindings)
                elif "event-gateway" in data["endpoints"]:
                    for event_endpoint in data["endpoints"]["event-gateway"]:
                        self.faas_bindings[event_endpoint["event-id"]] = event_endpoint["endpoint"]
                    logging.debug("FaaS Bindings ==>" + self.faas_bindings)
                elif "network-binding" in data["endpoints"]:
                   for network_endpoint in data["endpoints"]["network-binding"]:
                       self.network_bindings[network_endpoint["network-id"]] = event_endpoint["endpoint"]
                   logging.debug("Network Bindings ==>" + self.network_bindings)

                return True

            except socket.error:
                pass

        return False

    def connect(self, interface):
        interface = interface.split('.')[1]

        if interface in self.faas_bindings:
            # Create an ENSSession object for the connection
            session = ENSEventSession(self.app, self.cloudlet, interface, self.faas_bindings[interface])
            if session.connect():
                return session
            else:
                return None

        if interface in self.http_bindings:
            # Create an ENSHttpSession object for the connection
            session = ENSHttpSession(self.app, self.cloudlet, interface, self.http_bindings[interface])
            if session.connect():
                return session
            else:
                return None

        if interface in self.network_bindings:
            # Create an ENSNetworkSession object for the connection
            session = ENSNetworkSession(self.app, self.cloudlet, interface, self.network_bindings[interface])
            if session.connect():
                return session
            else:
                return None

        logging.error("Cannot connect to unknown interface %s" % interface)
        return None
