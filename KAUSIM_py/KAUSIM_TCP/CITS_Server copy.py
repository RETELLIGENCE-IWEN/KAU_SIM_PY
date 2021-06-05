import socket
from _thread import *



def threaded(client_socket, addr): 

    print('\nConnected by :', addr[0], ':', addr[1]) 



    # 클라이언트가 접속을 끊을 때 까지 반복합니다. 
    while True: 

        try:

            # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
            data = client_socket.recv(1024)
            # print("Request received - ", data.decode())
            # client_socket.sendall("Hello World".encode())

            if not data: 
                print('Disconnected by ' + addr[0],':',addr[1])
                break

            print('Received from ' + addr[0],':',addr[1] , data.decode())

            client_socket.send(data) 

        except ConnectionResetError as e:

            print('Disconnected by ' + addr[0],':',addr[1])
            break
        
        except ConnectionAbortedError as e:
            pass
             
    client_socket.close() 




# define
UNIT_STATUS   = 1
UNIT_LOCATION = 2
UNIT_BEACON   = 3
UNIT_CITS_T1  = 4
UNIT_CITS_T2  = 5
UNIT_CITS_T3  = 6
UNIT_CITS_T4  = 7


HOST = "127.0.0.1"
PORT = 60599
ConnectionEstablished = False


SS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

SS.bind((HOST, PORT))

SS.listen()

print("Waiting for Connection...")


# CL, clADDR = SS.accept()
# print("Server is connected by - ", clADDR)

while(1) : 

    CL, clADDR = SS.accept()
    start_new_thread(threaded, (CL, clADDR))



SS.close()