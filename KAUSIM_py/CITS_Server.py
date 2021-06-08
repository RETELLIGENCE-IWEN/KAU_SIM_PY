import sys
import socket
import time
from _thread import *

class CITS_SERVER:

    def __init__(self): # create socket

        self.HOST = "127.0.0.1"
        self.PORT = 60599
        self.ConnectionEstablished = False
        self.SS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Continue = True

        # define
        self.UNIT_STATUS   = 1
        self.UNIT_LOCATION = 2
        self.UNIT_BEACON   = 3
        self.UNIT_CITS_T1  = 4
        self.UNIT_CITS_T2  = 5
        self.UNIT_CITS_T3  = 6
        self.UNIT_CITS_T4  = 7

        #Types
        self.CITS_REQ_TYPE = ["CITS_Info_Vehicle", "CITS_Info_TrafficLight", "CITS_Info_Traffic_Stats", "CITS_Info_All_Traffic_Stats", "CITS_Info_Accident", "CITS_Info_FB_Distance"]


    # def SetUp(self):

        self.SS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SS.bind((self.HOST, self.PORT))
        self.SS.listen()

        print("Waiting for Connection...")

        # while(self.Continue) : 

        self.Client, self.clADDR = self.SS.accept()
        # start_new_thread(self.threaded, (CL, clADDR))
        # self.threaded(self.Client, self.clADDR)
        # self.SS.close()


    def CITS_Request(self, RQtype, RQID):
        
        # print("type : ", self.CITS_REQ_TYPE[RQtype])
        # print("packet : ", self.CITS_REQ_TYPE[RQtype] + ":" + RQID)

        data = self.CITS_REQ_TYPE[RQtype] + ":" + str(RQID)

        # len(data)
        # self.Client.sendall(int.to_bytes(len(data), 4, byteorder=sys.byteorder))
        # time.sleep(1)
        print("Sending : ", data)
        self.Client.sendall(data.encode())
        

        # while True: 

        try:
            data = self.Client.recv(1024)

            if not data: 
                print('Disconnected by ' + self.clADDR[0],':', self.clADDR[1])
                return()

            print('Received from ' + self.clADDR[0],':', self.clADDR[1] , data.decode())


        except ConnectionResetError as e:

            print('Disconnected')
            return()
        
        except ConnectionAbortedError as e:
            pass
        
    def CITS_Abort(self):
        self.SS.close()