# -*- coding: utf-8 -*- 

import logging
import time
import datetime
import httplib
import random
from threading import Thread, Lock

class SforNodeInfo:
    def __init__(self, host, port, check_path):
      self.host = host
      self.port = port
      self.check_path = check_path
      self.status = True
      self.lock = Lock()

    def disable(self):
      with self.lock:
        self.status = False
    
    def enable(self):
      with self.lock:
        self.status = True
    
def backend_check(check_list, loop=True, wait_time=15, http_timeout=3):
    while loop:
        for n in check_list:
            conn = httplib.HTTPConnection(n.host, n.port, timeout=http_timeout)
            conn.request("GET", n.check_path)
            res = conn.getresponse()
            logging.debug("sfor %s res: %d" % (n.host, n.status))
            if res.status != 200:
                logging.info("sfor disable %s" % n.host)
                n.disable()
            else:
                logging.info("sfor enable %s" % n.host)
                n.enable()

        time.sleep(wait_time)

class SforSimple:
    
    def __init__(self, node_list):
        self.node_list = node_list
        backend_check(node_list, False)
        th = Thread(target=backend_check, args=(node_list,))
        th.daemon = True
        th.start()
    
    def resolv(self):
        node_list = self.node_list
        
        rnd = random.randint(0, len(node_list) - 1)
        for i in range(len(node_list)):
            n = (i + rnd) % len(node_list) 
            info = node_list[n]
            stat = info.status
            if stat == True:
                return info.host
        return None

