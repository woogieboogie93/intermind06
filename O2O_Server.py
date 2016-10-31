# -*- coding: utf8 -*-
import logging, threading
import server_forever
import re
import sqlite3
import sys, os, commands
import pytesseract
from PIL import Image

db = sqlite3.connect('user.db')
db.text_factory = str

class O2O_Server(server_forever.Server):
    self.path = ''
    def handle(self):
        self.data = self.conn.recv(1024)
        if self.data:
            logging.debug('Received from {}: {}'.format(self.conn.getpeername(),self.data))
            request_msg = self.data.split()

            if((request_msg[0] == 'CHECK') and (requeset_msg[1] == 'LOGIN') and len(request_msg) == 4): # login 시도
                result = self.check_login(request_msg[2],request_msg[3])
                if result == 'success':
                    self.conn.sendall('200 OK '+ result + '\n')
                elif result == 'fail':
                    self.conn.sendall('405 Failed information'+ '\n')

            elif((request_msg[0] == 'CHECK') and (request_msg[1] == 'REGISTER') and len(request_msg) == 5): # register 시도
                result = self.check_register(request_msg[2],request_msg[3],request_msg[4])
                if result == 'Existent':
                    self.conn.sendall('400 Already existed in\n')
                elif result == 'Success':
                    self.conn.sendall('200 OK\n')

            elif((request_msg[0] == 'SERVICE') and (request_msg[1] == 'IMAGE') and len(request_msg) == 2):
                self.conn.sendall('210 Ready to Receive\n')
                result = self.get_image()
                success = result[0]
                self.path = result[1]
                if success == 1:
                    self.conn.sendall('200 OK\n')
                else:
                    self.conn.sendall('410 Failed load image\n')

            
            
        pass


#--------------------------------------------------------------------------------------------------------------------------------#
    def check_login(self,id,password): # 로그인 시 -> id와 password를 db에서 확인하여 로그인 처리
        # db에서 id와 password 검사하는 코드짜기
        cursor = db.cursor()
        template = "SELECT ID,PASSWORD FROM login_info WHERE ID="
        check = cursor.execute(template+id) # tuple로 나옴
        if check[1] == password:
            return 'success'
        else:
            return 'fail' ########################## 아이디가 없을경우 질의문이 돌아가는지 꼭 검사해볼 것 

    def check_register(self,id,password,name):
        cursor = db.cursor()
        template = "SELECT ID FROM login_info WHERE ID=" #db에 id가 있는지 검사
        check = cursor.execute(template+id) # tuple형태로 나옴
        if check[0] == id: # db에 가입하려는 id가 있을 때 
            return 'Existent' 
        else: #db에 가입하려는 id가 없을 때 해당 정보를 모두 저장
            template = "INSERT INTO login_info VALUES(%s,%s,%s)"
            cursor.execute(template%(id,password,name))
            db.commit()
            #db.close()
            return 'Success'

    def get_image(self):
        f = open('image.png','wb')
        while True:
            try:
                data = self.conn.recv(20000)
                img = img + data
                if data == None:
                    break
            except:
                AttributeError
                return (0,'')
        f.write(img)
        f.close()
        return (1,'image.png') # (이미지 업로드 성공 여부, 사진 경로)

        
            


    ###################def preprocessing(id,path) -> id와 업로드 한 사진 받아와 전처리 과정
    
    ###################def convert_tesseract() -> 전처리된 사진에 대해 id와

    ###################def make_traineddata()  -> 아이디와 그에 해당하는 traind data만들기

#--------------------------------------------------------------------------------------------------------------------------------#
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    server = O2O_Server('192.168.0.11',8888)
    server.serve()
