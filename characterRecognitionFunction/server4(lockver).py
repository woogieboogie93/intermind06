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
#from postprocess import postprocess
from trainTransaction import makeTraineddata
import string
import dictionary

#db = sqlite3.connect('user1.db',check_same_thread = False)
#db.text_factory = str #??

class Server(threading.Thread):
    def __init__(self,IP,PORT):
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
        self.lock = threading.Lock()
        self.dicLock = threading.Lock()


    def handler(self, clientsock, addr):
      u_id = ''
      try:
        while 1:
            time.sleep(1)
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
                        u_id = request_msg[2]
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
               clientsock.send('Empty')
               
            elif request_msg[0] == 'Train' and request_msg[1] == 'Image':
               angle = request_msg[2]
               print "angle: " + angle
               clientsock.send('200 OK confirm')
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
               
      finally:
          logging.info('Client closing {}'.format(addr))
          clientsock.close()
          del threads[u_id]
          print threads

## recv train image          
    def receive_train_image(self,clientsock,addr,angle):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        print 'userid list?? ',user_id
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            train_num = cursor.fetchone()
            db.commit()
            db.close()
            
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
             print '410'
             clientsock.send('410 Failed load image')
             print 'failed finish rotate' 
        elif rotate_result == 'Rotate Success':
             print 'success finish rotate' 
             result_train = self.train('r_'+user_id[0]+'.jpg',user_id[0],train_num[0])
             print '200'
             if result_train == -1:
                 print '425 failed train'
                 clientsock.send("425 Failed train")
             else:
                 print "success train"
                 clientsock.send('200 OK train')
        
## recv recognition image
    def receive_recognition_image(self,clientsock,addr,angle):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            train_num = cursor.fetchone()
            print 'traineddata count = ' + str(train_num)
            db.commit()
            db.close()
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
            print '410'
            clientsock.send('410 Failed load image')
            print 'failed finish rotate'
        elif rotate_result == 'Rotate Success':
            print 'success finish rotate'
            result = self.recognize(clientsock, addr, 'r_'+user_id[0]+'.jpg',user_id[0],train_num[0])
            if result == 0:
                print 'success recognition'
                clientsock.send("200 OK recognition")
                print 'send 다함~'
            else:
                print 'failed recognition'
                clientsock.send("425 Failed recognition")
         
    def check_login(self,user_id,password):
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            template = "SELECT user_id,password FROM User_Info WHERE user_id="
            cursor.execute(template+"'"+user_id+"'")
            check = cursor.fetchone()
            db.commit()
            db.close()
        if check == None:
            return 'fail'
        else:
            
            if check[1] == password:
                return 'success'
            else:
                return 'fail'

    def check_registering(self,user_id,password,email):
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            template = "SELECT user_id FROM User_Info WHERE user_id="
            cursor.execute(template+"'"+user_id+"'")
            check = cursor.fetchone()
            if check != None:
                db.commit()
                db.close()
                return 'Existent'
            else:
                template2 = "INSERT INTO User_Info VALUES(%s,%s,%s,%s)" # id,password,email,trained_count
                cursor.execute(template2%("'"+user_id+"'","'"+password+"'","'"+email+"'",0))
                db.commit()
                db.close()
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
                with self.lock:
                    db = sqlite3.connect('user1.db',check_same_thread = False)
                    c = db.cursor()
                    c.execute('update User_Info set train_count = train_count + 1 where user_id = ?',(userID,))
                    db.commit()
                    db.close()
                    return 0
        # train 실패
        return -1

    def recognize(self, clientsock,addr,filename, userID, traineddata):
        data = ''
        if preprocess(filename, userID, traineddata) == 0:
            filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
            if recognizeCharacter(filename, userID, traineddata) == 0:
                print 'zz'
                filename = userID + str(traineddata) + '.txt'
                print 'zzz'
                result = self.postprocess(filename)
                print result
                if result == 0:
                    print 'zzzz'
                    filname = userID + str(traineddata) + '.md'
                    print 'filename = ', filename
                    f = open(filename, 'rb')
                    data = f.read()
                    print 'server send : ', data
                    #clientsock.send(data)
                    print 'send OK'
                    # 성공.
                    f.close()
                    return 0 
                else:
                    return -1
        # 실패 시 어떠한 행동을 취해야 할지
        else:
            return -1

    def postprocess(self, filename):
        self.heuristic(filename)
        print 'a'
        filename = filename.split('.')
        filename = '.'.join(filename[:-1]) + '.md'
        print 'b'
        return self.referToDictionary(filename)

    def heuristic(self, filename):

        whitespace = ['\t', '\n', '\r', '\f', '\v', ' ']
        lowerToUpper = {'o':'O', 'p':'P', 'l':'I', 'x':'X', 'v':'V', 'z':'Z'}
        upperToLower = {'O':'o', 'P':'p', 'I':'l', 'X':'x', 'V':'v', 'Z':'z'}

        case = [punc + space for punc in ['.', '!', '?'] for space in whitespace]

        try:
            f = open(filename, 'r')
        except:
            return -1
        content = f.read()

        f.close()

        content = list(content)

        if content[0] in lowerToUpper.keys():
            content[0] = lowerToUpper[content[0]]

        if content[1] in lowerToUpper.keys():
            if content[0] in whitespace:
                content[1] = lowerToUpper[content[1]]
        if content[1] in upperToLower.keys():
            if content[0] not in whitespace:
                content[1] = upperToLower[content[1]]

        for i in range(2, len(content)):
            if content[i] in lowerToUpper.keys():
                if content[i - 2] + content[i - 1] in case:
                    content[i] = lowerToUpper[content[i]]
            if content[i] in upperToLower.keys():
                if content[i - 2] + content[i - 1] not in case:
                    content[i] = upperToLower[content[i]]

        content = ''.join(content)

        filename = filename.split('.')
        filename = '.'.join(filename[:-1]) + '.md'
        #print filename
            
        f = open(filename, 'w')

        f.write(content)

        f.close()

        return 0

# 
    def referToDictionary(self, filename):

        try:
            f = open(filename)
            print 'd'
        except:
            return -1

        try:
            origin = '\n'.join([unicode(line, errors = 'ignore') for line in f.readlines()])
            print 'e'
            f.close()
        except:
            return -1
        words = origin

        punc = list(string.punctuation+string.whitespace) 
        for i in punc:
            words = words.replace(i,' ')

        newWords = [word for word in words.split(' ') if len(word) > 1 ]
        words = [word for word in words.split(' ') if len(word) > 1 ]
    
        print 'f'

        dic = dictionary.Dictionary()
        with self.dicLock:
            conn = sqlite3.connect('wordFrequency.db')
            c = conn.cursor()
            try:
                c.execute('''create table words (word text, frequency real)''')
                conn.commit()
                conn.close()
            except: pass

        print 'g'
        print words

        for word in words:
            if not dic.isInDictionary(word) and len(word) > 1:
                try:
                    similarWords = dic.getSimilarWords(word)
                    wordFrequency = []
                    print 'dudududu'
                    for similarWord in similarWords:
                        with self.dicLock:
                            conn = sqlite3.connect('wordFrequency.db')
                            c = conn.cursor()
                            c.execute('select * from words where word = ?', (similarWord,))
                            frequency = c.fetchone()
                            conn.commit()
                            conn.close()
                        if frequency != None:
                            wordFrequency.append(frequency)
                    print 'dudududu2'
                    if wordFrequency == []:
                        origin = origin.replace(word, similarWords[0])
                        word = similarWords[0]
                        print 'dudududu3'
                    else:
                        sorted(wordFrequency, key = lambda x: x[1])
                        origin = origin.replace(word, wordFrequency[0][0])
                        print 'dudududu4'
                        with self.dicLock:
                            conn = sqlite3.connect('wordFrequency.db')
                            c = conn.cursor()
                            c.execute('update words set frequency = frequency + 1 where word = ?',(wordFrequency[0][0]))
                            conn.commit()
                            conn.close()
                        print 'dudududu5'
                        newWords.remove(word)
                except: pass
            else :
                with self.dicLock:
                    conn = sqlite3.connect('wordFrequency.db')
                    c = conn.cursor()
                    c.execute('select * from words where word = ?', (word,))
                    if c.fetchone():
                        c.execute('update words set frequency = frequency + 1 where word = ?',(word,))#####
                        newWords.remove(word)
                    conn.commit()
                    conn.close()

        words = newWords

        print '?'

        with self.dicLock:
            print '??'
            conn = sqlite3.connect('wordFrequency.db')
            print '???'
            c = conn.cursor()
            for word in words:
                c.execute('insert into words values (?,?)', (word, 1))
                print '????'
            conn.commit()
            conn.close()

        print 'h'


        f = open(filename,'w')
        f.write(origin.encode('utf8'))
        f.close()
    
        return 0

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
   print threads
