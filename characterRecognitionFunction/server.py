import threading
from socket import *
import time
import logging
import re
import sqlite3
import sys, os, commands
import time
from PIL import Image
#import pytesseract
#from PIL import Image

db = sqlite3.connect('user.db',check_same_thread = False)
db.text_factory = str

class Server(threading.Thread):
    def __init__(self,IP,PORT):
        threading.Thread.__init__(self)
        self.ip = IP
        self.port = PORT
        request_msg = []
        ADDR = (self.ip, self.port)
        self.serversocket = socket(AF_INET, SOCK_STREAM)
        self.serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serversocket.bind(ADDR)
        self.serversocket.listen(10)
        self.angle = '0'
        self.rotate_result = ''

    def run(self):
        while 1:
            print 'waiting for connection...'
            self.clientsock, self.addr = self.serversocket.accept()
            print '...connected from:', self.addr
            time.sleep(1)
            self.handler()

    def handler(self):
     #   self.clientsock = clientsock
      #  self.addr = addr
        while 1:
            time.sleep(1)
            data = self.clientsock.recv(1000000)
            request_msg = data.split()
            time.sleep(1)
            #print 'data: ' + repr(request_msg)
            if not data: break
            if request_msg[0] == 'CHECK' and request_msg[1] == 'LOGIN':
               if request_msg[2] == '1' and request_msg[3] == '1':
                   print 'server recv: client login'
                   self.clientsock.send('200 OK')
               else:
                   print 'server recv: client login dismatch'
                   self.clientsock.send('Not Correct')
                   
            elif request_msg[0] == 'CHECK' and request_msg[1] == 'REGISTERING':
               if len(request_msg) == 5:
                   print 'server recv: client registering'
                   self.clientsock.send('REGISTERING SUCCESS')
               else:
                   print 'server fail'
                   self.clientsock.send('REGISTERING FAIL')
                   
            elif request_msg[0] == 'Empty':
               print 'server recv: Empty'
               self.clientsock.send('Empty')
               
            elif request_msg[0] == 'Upload':
               print 'server recv: Upload'
               self.clientsock.send('Upload')
               
            elif request_msg[0] == 'Camera':
               print 'server recv: Camera'
               self.clientsock.send('Camera')
               
            elif request_msg[0] == 'Train' and request_msg[1] == 'Image':
               self.angle = request_msg[2]
               print "angle: " + self.angle
               self.clientsock.send('200 OK Confirm')
               time.sleep(0.5)
               print 'server recv: Confirm'
               f = open('image2.jpg','wb')
               while(True):
                  data2 = self.clientsock.recv(1000000)
                  if data2[-1] == '\\':
                      f.write(data2)
                      break
                  f.write(data2)
               f.close()
               print 'finish receive'
               time.sleep(2)
               #print self.rotate('image2.jpg',self.angle)
               if self.rotate_result == 'Rotate_Fail':
                   self.clientsock.send('425 Failed train')
               elif self.rotate_result == 'Rotate_Success':
                   self.clientsock.send('200 OK train')
        #self.clientsock.close()         


    def check_login(self,user_id,password):
        cursor = db.cursor()
        template = "SELECT user_id,password FROM User_Info WHERE user_id="
        cursor.execute(template+"'"+user_id+"'")
        check = cursor.fetchone()
        if check == None:
            return 'fail'
        else:
            if check[1] == password:
                return 'success'
            else:
                return 'fail'

    def check_registering(self,user_id,password,email):
        cursor = db.cursor()
        template = "SELECT user_id FROM User_Info WHERE user_id="
        cursor.execute(template+"'"+user_id+"'")
        check = cursor.fetchone()
        if check != None:
            return 'Existent'
        else:
            template2 = "INSERT INTO User_Info VALUES(%s,%s,%s,%s)" # id,password,email,trained_count
            cursor.execute(template2%("'"+user_id+"'","'"+password+"'","'"+email+"'",0))
            db.commit()
            #db.close()
            return 'Success'

    def rotate(self, filename, angle):
        try :
            im = Image.open(filename)
            if angle == '90':
                im2 = im.transpose(Image.ROTATE_270)
                im2.save('output.jpg')
            elif angle == '180':
                im2 = im.transpose(Image.ROTATE_180)
                im2.save('output.jpg')
            elif angle == '270':
                im2 = im.transpose(Image.ROTATE_90)
                im2.save('output.jpg')
            elif angle == '0':
                im.save('output.jpg')
            #im2 = im.rotate(-int(angle))
        except IOError:
            return 'Rotate Fail'
        return 'Rotate Success'
    
threads = []

if __name__ == '__main__':
   thread = Server("203.253.76.79", 9015)
   thread.start()
   threads.append(thread)
   for thread in threads:
       thread.join()
