import sys
import socket

HOST = '192.168.0.21'
PORT = 8897

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'socket created'

try:
    s.bind((HOST,PORT))
except socket.error as err:
    print 'Bind Failed, Error Code: ' + str(err[0])+', Message: '+err[1]
    sys.exit()

print 'Socket Bind Success!'

s.listen(10)
print 'Socket is now listening'

while 1:
    print 'tt'
    conn,addr=s.accept()
    print 'd'
    print 'Connect with ' +addr[0]+':'+str(addr[1])
    buf = conn.recv(64)
    print buf
s.close()
