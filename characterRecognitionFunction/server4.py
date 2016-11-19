#_*_coding: utf-8

import threading
from socket import *
import time
import logging
import re
import sqlite3
import sys, os, commands
import time
from PIL import Image
#import select
from preprocess import preprocess
from characterRecognition import recognizeCharacter
from postprocess import postprocess
from trainTransaction import makeTraineddata 

db = sqlite3.connect('user1.db',check_same_thread = False)
db.text_factory = str

class Server(threading.Thread):
    def __init__(self,IP,PORT):
       # threading.Thread.__init__(self)
        self.ip = IP
        self.port = PORT
        request_msg = []
        ADDR = (self.ip, self.port)
        self.serversocket = socket(AF_INET, SOCK_STREAM)
        self.serversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.serversocket.bind(ADDR)
        self.serversocket.listen(10)
        self.serversocket.setsockopt(SOL_SOCKET, SO_RCVBUF, 10000000)
        self.serversocket.setsockopt(SOL_SOCKET, SO_SNDBUF, 10000000)
        self.sendsize = self.serversocket.getsockopt(SOL_SOCKET,SO_SNDBUF)
        self.rcvsize = self.serversocket.getsockopt(SOL_SOCKET,SO_RCVBUF)
       # self.lock = threading.Lock()
        #self.angle = '0'
        #self.rotate_result = ''


    def handler(self, clientsock, addr):
       #self.clientsock = clientsock
       #self.addr = addr
      try:
        while 1:
            time.sleep(1)
            #data = self.clientsock.recv(1000000)
            data = clientsock.recv(1000000)
            request_msg = data.split()
            time.sleep(1)
            #print 'data: ' + repr(request_msg)
            if not data: break
            if ((request_msg[0] == 'CHECK') and (request_msg[1] == 'LOGIN')):
                if len(request_msg) != 4:
                    clientsock.send('404 Less information')
                else:
                    result = self.check_login(request_msg[2],request_msg[3])
                    if result == 'success':
                        print 'server recv: client login'
                        print 'send: '+str(self.sendsize)
                        print 'receive: '+str(self.rcvsize)
                        clientsock.send('200 OK')
                        threads[request_msg[2]]=addr
                    elif result == 'fail':
                        print 'server recv: client fail login'
                        clientsock.send('405 Failed information')
                        
            elif request_msg[0] == 'CHECK' and request_msg[1] == 'REGISTERING':
                if len(request_msg) == 5:
                    result = self.check_registering(request_msg[2],request_msg[3],request_msg[4])
                    if result == 'Existent':
                        print 'server recv: client fail registering'
                        clientsock.send('400 Already existed in')
                    elif result == 'Success':
                        print 'server recv: client registering'
                        clientsock.send('200 OK')
                else:
                    clientsock.send('404 Less information')
                   
            elif request_msg[0] == 'Empty':
               print 'server recv: Empty'
               #self.clientsock.send('Empty')
               clientsock.send('Empty')
               
            elif request_msg[0] == 'Upload':
               print 'server recv: Upload'
               #self.clientsock.send('Upload')
               clientsock.send('Upload')
               
            elif request_msg[0] == 'Camera':
               print 'server recv: Camera'
               #self.clientsock.send('Camera')
               clientsock.send('Camera')
               
            elif request_msg[0] == 'Train' and request_msg[1] == 'Image':
               angle = request_msg[2]
               print "angle: " + angle
               clientsock.send('200 OK confirm')
               #clientsock.send('200 OK')
               time.sleep(0.5)
               print 'server recv: Confirm'
               self.receive_train_image(clientsock,addr,angle)
               #time.sleep(2)

            elif request_msg[0] == 'Recognition' and request_msg[1] == 'Image':
               angle = request_msg[2]
               print "angle: " + angle
               clientsock.send('200 OK confirm')
               time.sleep(0.5)
               print 'server recv: Recognition'
               self.receive_recognition_image(clientsock, addr, angle)               
        #self.clientsock.close()
               
      finally:
          logging.info('Client closing {}'.format(addr))
          #self.clientsock.close()
          clientsock.close()

## recv train image          
    def receive_train_image(self,clientsock,addr,angle):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        cursor = db.cursor()
        cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
        train_num = cursor.fetchone()        
        f = open(user_id[0]+'.jpg','wb')
        print 'open'
        while(True):
            print '1111'
            data2 = clientsock.recv(1000000)
            print '2222'
            if data2[-1] == ' ':
                f.write(data2)
                print '44444'
                break
            f.write(data2)
            print '3333'   
        f.close()
        
        print 'finish receive'
        
        time.sleep(2)
        rotate_result = self.rotate(user_id[0]+'.jpg',angle)
        
        print rotate_result
        if rotate_result == 'Rotate Fail':
             print '425'
             clientsock.send('425 Failed train')
             print 'finish rotate' 
        elif rotate_result == 'Rotate Success':
             print '200'
             clientsock.send('200 OK train')
             print 'finish rotate' 
             result_train = self.train('r_'+user_id[0]+'.jpg',user_id[0],train_num[0])
             print result_train
        #print 'finish rotate' 
        
## recv recognition image
    def receive_recognition_image(self,clientsock,addr,angle):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        cursor = db.cursor()
        cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
        train_num = cursor.fetchone()        
        f = open(user_id[0]+'.jpg','wb')
        while(True):
            print '1'
            data2 = clientsock.recv(1000000)
            print '2' 
            if data2[-1] == ' ':
                print '4'
                f.write(data2)
                print 'Server recv EOF..'
                break
            f.write(data2)
            print'3'
        f.close()
        print 'finish receive'
        
        time.sleep(2)
        rotate_result = self.rotate(user_id[0]+'.jpg',angle)

        print rotate_result
        if rotate_result == 'Rotate Fail':
             print '425'
             clientsock.send('425 Failed train')
             print 'finish rotate'
        elif rotate_result == 'Rotate Success':
             print '200'
             clientsock.send('200 OK train')
             print 'finish rotate'
             self.recognize('r_'+user_id[0]+'.jpg',user_id[0],train_num[0])
         
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
                im2.save('r_'+filename)
            elif angle == '180':
                im2 = im.transpose(Image.ROTATE_180)
                im2.save('r_'+filename)
            elif angle == '270':
                im2 = im.transpose(Image.ROTATE_90)
                im2.save('r_'+filename)
            elif angle == '0':
                im.save('r_'+filename)
            #im2 = im.rotate(-int(angle))
        except IOError:
            print 'IOError to rotate'
            return 'Rotate Fail'
        return 'Rotate Success'
    
    def start(self):
        logging.info('Server started')
        while True:
            #self.clientsock, self.addr = self.serversocket.accept()
            clientsock, addr = self.serversocket.accept()
            logging.info('Connected by {}'.format(addr))
            thread_handler = threading.Thread(target = self.handler, args = (clientsock, addr))
            thread_handler.daemon = True
            thread_handler.start()
            
    def train(self, filename, userID, traineddata):
        if preprocess(filename, userID, traineddata) == 0:
            filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
            if makeTraineddata(filename, userID, traineddata) == 0:
                # train 성공! traineddata + 1
                c = db.cursor()
                c.execute('update User_Info set train_count = train_count + 1 where user_id = ?',(userID,))
                return 0
        # train 실패
        return -1

    def recognize(self, filename, userID, traineddata):
        if preprocess(filename, userID, traineddata) == 0:
            filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
            if recognizeCharacter(filename, userID, traineddata) == 0:
                filename = userID + str(traineddata) + '.txt'
                postprocess(filename)
                filname = userID + str(traineddata) + '.md'
                f.open(filename, 'rb')
                data = f.read()
                clientsock.send(data) # .md 내용 전송
                # 성공. 
                return 0
        # 실패 시 어떠한 행동을 취해야 할지
        return -1
threads = {}
if __name__ == '__main__':
   #thread = Server("203.253.76.79", 9015)
   #thread.start()
   #threads.append(thread)
   #for thread in threads:
   #    thread.join() 
   logging.basicConfig(filename ='', level=logging.INFO)
   server = Server("203.253.76.79", 9015)
   server.start()
