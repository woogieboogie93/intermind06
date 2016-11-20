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
import string
import dictionary
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email import Utils
from email.header import Header

#db = sqlite3.connect('user1.db',check_same_thread = False)
#db.text_factory = str #??

smtp_server =  "smtp.gmail.com"
port = 587
O2O_email = "intermind06@gmail.com"
O2O_password = "1p2o3i4u5y6t7r8e9w0q"

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
        self.server_train_string = [
            "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGthequickbrownfoxjumpsoverthelazydog1234567890#>.*+-][",
            "BRICKQUIZWHANGSJUMPYVELDTFOXbrickquizwhangsjumpyveldtfox1234567890#>.*+-][",
            "JACKDAWSLOVEMYSPHINXOFBLACKQUARTZjackdawslovemysphinxofblackquartz1234567890#>.*+-][",
            "THEFIVEBOXINGWIZARDSJUMPEDQUICKLYthefiveboxingwizardsjumpedquickly1234567890#>.*+-][",
            "MANYWIVEDJACKJAUGHSATPROBESOFSeXQUIZmanywivedjacklaughsatprobesofsexquiz1234567890#>.*+-][",
            "FIVEBIGQUACKINGZEPHYRSJOLTMYWAXBEDfivebigquackingzephyrsjoltmywaxbed1234567890#>.*+-][",
            "HICKJEDWINSQUIZFOREXTRABLIMPVOYAGEhickjedwinsquizforextrablimpvoyage1234567890#>.*+-][",
            "SYMPATHIZINGWOULDFIXQUAKEROBJECTIVESsympathizingwouldfixquakerobjectives1234567890#>.*+-][",
            "BRAWNYGODSJUSTFLOCKEDUPTOQUIZANDVEXHIMbrawnygodsjustflockeduptoquizandvexhim1234567890#>.*+-][",
            "JIMJUSTQUITANDPACKEDEXTRABAGSFORLIZQWENjimjustquitandpackedextrabagsforlizqwen1234567890#>.*+-]["
            ]
        
        self.user_train_string = [
            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG\nthe quick brown fox jumps over the lazy dog\n1234567890\n#>.*+-][",
            "BRICK QUIZ WHANGS JUMPY VELDT FOX\nbrick quiz whangs jumpy veldt fox\n1234567890\n#>.*+-][",
            "JACKDAWS LOVE MY SPHINX OF BLACK QUARTZ\njackdaws love my sphinx of black quartz\n1234567890\n#>.*+-][",
            "THE FIVE BOXING WIZARDS JUMPED QUICKLY\nthe five boxing wizards jumped quickly\n1234567890\n#>.*+-][",
            "MANY WIVED JACK LAUGHS AT PROBES OF SEX QUIZ\nmany wived jack laughs at probes of sex quiz\n1234567890\n#>.*+-][",
            "FIVE BIG QUACKING ZEPHYRSJOLT MY WAX BED\nfive big quacking zephyrsjolt my waxbed\n1234567890\n#>.*+-][",
            "HICK JED WINS QUIZ FOR EXTRA BLIMP VOYAGE\nhick jed wins quiz for extra blimp voyage1234567890#>.*+-][",
            "SYMPATHIZING WOULD FIX QUAKER OBJECTIVES\nsympathizing would fix quaker objectives\n1234567890\n#>.*+-][",
            "BRAWNY GODS JUST FLOCKED UP TO QUIZ AND VEX HIM\nbrawny gods just flocked up to quiz and vex him\n1234567890\n#>.*+-][",
            "JIM JUST QUIT AND PACKED EXTRA BAGS FOR LIZ QWEN\njim just quit and packed extra bags for liz qwen\n1234567890\n#>.*+-]["
            ]

    def handler(self, clientsock, addr):
      #u_id = ''
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
                        #u_id = request_msg[2]
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
               self.receive_train_image(clientsock, addr, angle)
               #time.sleep(2)

            elif request_msg[0] == 'Train' and request_msg[1] == 'String':
               self.send_train_string(clientsock,addr)

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
          #del threads[u_id]
          print threads

## recv train string
    def send_train_string(self, clientsock, addr):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        #print 'userid list?? ',user_id
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            train_num = cursor.fetchone()
            db.commit()
            db.close()
        
        clientsock.send('200 OK String %s' % self.user_train_string[train_num[0] % 10])

## recv train image          
    def receive_train_image(self,clientsock,addr,angle):
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            user_id = [a[0] for a in threads.items() if a[1] == addr]
            cursor = db.cursor() ############
            cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            train_num = cursor.fetchone()
            db.commit()
            db.close

            ()
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
             print 'finish rotate' 
             result_train = self.train('r_'+user_id[0]+'.jpg',user_id[0],train_num[0])
             print result_train
             if result_train == 0:
                 print '200'
                 clientsock.send('200 OK train')
             elif result_train == -1:
                 clientsock.send('425 Failed train')
             
        #print 'finish rotate' 
               
## recv recognition image
    def receive_recognition_image(self,clientsock,addr,angle):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            cursor.execute("SELECT email,train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            info = cursor.fetchone()
            print 'traineddata count = ' + str(info[1])
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
            #clientsock.send("200 OK recognition")######################################
            result = self.recognize(clientsock, addr, 'r_'+user_id[0]+'.jpg',user_id[0],info[1],info[0])
            if result == 0:
                print 'success recognition'
                time.sleep(1)
                clientsock.send("200 OK recognition")#########################################################
                print 'send 다함~'
                time.sleep(1)

                data = clientsock.recv(4092)
                print 'data ======', data
                if data == 'Ready\n':

                    self.send_md_file(clientsock, addr, user_id[0]+str(info[1])+'.md')
                                    
                    # recognized 된 md문서를 사용자 이메일로 전송
                    subject = '<O2O Editor>요청하신 인식된 파일 입니다. '
                    text = '''안녕하세요. O2O Editor 입니다.\nO2O Editor를 이용해주셔서 진심으로 감사 드립니다.
                        요청하신 사진에 대한 문서 파일 입니다. 첨부파일을 확인하세요.
                        이용해 주셔서 감사합니다.'''
                    attach = user_id[0]+str(info[1])+'.md' ##############################################
                    user_email = info[0]
                    self.send_mail(O2O_email,user_email,subject,text,attach)
            else:
                print 'failed recognition'
                clientsock.send("425 Failed recognition")

    def send_md_file(self,clientsock, addr, filename):
        print 'data는 ready'
        f = open(filename, 'rb')
        data2 = f.read()
        #print len(data2)
        print 'data2 ==' , data2
        clientsock.send(data2)
        print '잘 보냄'
        f.close()
         
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

    def send_string(self, userID):
        user_id = [a[0] for a in threads.items() if a[1] == addr]
        print 'userid list?? ',user_id
        with self.lock:
            db = sqlite3.connect('user1.db',check_same_thread = False)
            cursor = db.cursor()
            cursor.execute("SELECT train_count FROM User_Info WHERE user_id='"+user_id[0]+"'")
            train_num = cursor.fetchone()
            db.commit()
            db.close()
        return train_num % 10
    
    def train(self, filename, userID, traineddata):
        if preprocess(filename, userID, traineddata) == 0:
            filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
            
            if makeTraineddata(filename, userID, traineddata, self.server_train_string[traineddata % 10]) == 0:
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

    def recognize(self, clientsock,addr,filename, userID, traineddata,user_email):
        data = ''
        if preprocess(filename, userID, traineddata) == 0:
            filename = userID + str(traineddata) + '.o2oEditor.exp0.tif'
            if recognizeCharacter(filename, userID, traineddata) == 0:
                print 'zz'
                filename = userID + str(traineddata) + '.txt'
                print 'zzz'
                result = postprocess(filename)
                print result
                if result == 0:
                    print 'zzzz'
                    filname = userID + str(traineddata) + '.md'
                    return 0 
                else:
                    return -1
        # 실패 시 어떠한 행동을 취해야 할지
        else:
            return -1
        
    def send_mail(self,O2O_email,user_email,subject,text,attach):
        msg = MIMEMultipart("alternative")
        msg["From"] = O2O_email
        msg["To"] = user_email
        msg["Subject"] = Header(s=subject,charset="utf-8")
        msg["Date"] = Utils.formatdate(localtime = 1)
        msg.attach(MIMEText(text,"html",_charset="utf-8"))

        if(attach!=None):
            part = MIMEBase("application","octet-stream")
            part.set_payload(open(attach,'rb').read())
            Encoders.encode_base64(part)
            part.add_header("Content-Disposition","attachment;filename=\"%s\"" % os.path.basename(attach))
            msg.attach(part)

        smtp = smtplib.SMTP(smtp_server,port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(O2O_email,O2O_password)
        smtp.sendmail(O2O_email,user_email,msg.as_string())
        smtp.close()

        
threads = {}
if __name__ == '__main__':
   #thread = Server("203.253.76.79", 9015)
   #thread.start()
   #threads.append(thread)
   #for thread in threads:
   #    thread.join() 
   logging.basicConfig(filename ='', level=logging.INFO)
   server = Server("203.253.76.79", 9016)
   server.start()
   #print threads
