# RETELLIGENCE

import socket

# define
UNIT_STATUS   = 1
UNIT_LOCATION = 2
UNIT_BEACON   = 3
UNIT_CITS_T1  = 4
UNIT_CITS_T2  = 5
UNIT_CITS_T3  = 6
UNIT_CITS_T4  = 7

class KAUSIM_TCP_Client:

    def __init__(self): # create client socket
        self.HOST = "127.0.0.1"
        self.PORT = 60599
        # self.PORT = 9737
        self.ConnectionEstablished = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def Connect2Server(self): # connect to server socket

        # connect to server
        try :
            self.client_socket.connect((self.HOST, self.PORT))
            self.ConnectionEstablished = True
            

        except ConnectionAbortedError as e:
            self.ConnectionEstablished = False
            print(e)


        except ConnectionError as e:
            self.ConnectionEstablished = False
            print(e)

        except ConnectionRefusedError as e:
            self.ConnectionEstablished = False
            print(e)

        except ConnectionResetError as e:
            self.ConnectionEstablished = False
            print(e)
            
        finally : return(self.ConnectionEstablished)


    def FireRequest(self, _request): # send request and wait for answer

        if not self.ConnectionEstablished : return(False)

        try :

            # receive
            data = (self.client_socket.recv(1024)).decode()
            # print(data)

            _request = "Answer"
            # send request
            self.client_socket.sendall(_request.encode())
            return(data)

        except ConnectionAbortedError as e:
            return(False)


    def TerminateConnection(self):
        try :
            self.client_socket.close()
        except :
            pass








# My = KAUSIM_TCP_Client()
# r = My.Connect2Server()
# print(r)

# My.FireRequest(1)
# # My.FireRequest(1)
# # My.FireRequest(1)
# # My.FireRequest(1)

# My.TerminateConnection()