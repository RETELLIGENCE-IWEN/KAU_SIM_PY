import sys
import socket
import time
from _thread import *


HOST = "127.0.0.1"
PORT = 60599
ConnectionEstablished = False

SS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SS.bind((HOST, PORT))
SS.listen()

print("Waiting for Connection...")

Client, clADDR = SS.accept()

print("Connection Established")
while(1):
    data = Client.recv(1024)
    
    if not data: 
        print('Disconnected by ' + clADDR[0],':', clADDR[1])
        break

    print('Received from ' + clADDR[0],':', clADDR[1] , data.decode())


SS.close()