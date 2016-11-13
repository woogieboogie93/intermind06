#_*_coding: utf-8

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from email import Utils
from email.header import Header
import os

smtp_server =  "smtp.gmail.com"
port = 587
O2O_email = "intermind06@gmail.com"
O2O_password = "1p2o3i4u5y6t7r8e9w0q"
#O2O_email = '94young1206@gmail.com'
#O2O_password = 'duddms11'

def send_mail(O2O_email,user_email,subject,text,attach):
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

        
if __name__ == '__main__':
    send_mail(O2O_email,'94young1206@naver.com','제목-발송','내용-확인','test.txt')
    print 'hh'
