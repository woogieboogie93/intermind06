# -*- coding: utf-8 -*-
"""
Created on Wed October 25 1:30:34 2016

@author: Kwon YoungEun
"""

from socket import *
import select
import logging

class Server():

    def __init__(self,my_Ip,my_port):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)
        self.sock.bind((my_Ip, my_port))
        self.sock.listen(5)
        self.read_socks = [self.sock]
        
    def handle(self):
        pass
        
    def serve(self):
        logging.info('Server started')
        while True:
            readables, _, _ = select.select(self.read_socks, [], [])
            for sockobj in readables:
                if sockobj is self.sock:
                    conn, cli_addr = self.sock.accept()
                    self.read_socks.append(conn)
                    logging.info('Connected by {}'.format(cli_addr))
                else:
                    self.conn = sockobj
                    try:
                        self.handle()
                    except IOError as e:
                        logging.exception('socket error: {}'.format(e))
                        self.read_socks.remove(self.conn)
                        self.conn.close()
                    else:
                        if not self.data:    
                            logging.info('Client closing {}'.format(self.conn.getpeername()))
                            self.read_socks.remove(sockobj)
                            self.conn.close()
                        
