import KSIM_tcpClient
import time



MyClient = KSIM_tcpClient.KAUSIM_TCP_Client()


# Connection
ConnectionTryOut = 10
Connected = False

while(ConnectionTryOut > 0) :
    if MyClient.Connect2Server() : 
        Connected = True
        print("Connected to Server Succes")
        break

    else :
        print("$ Connection Denied - Reconnecting in 3 seconds - Atempt : ", 11 - ConnectionTryOut) 
        ConnectionTryOut -= 1
        time.sleep(3)
        
        

if Connected :

    while(1):

        try :
            data = MyClient.FireRequest(KSIM_tcpClient.UNIT_STATUS)
            print(data)

        except : pass

        finally : pass





else : print("Failed to connect to server")


# MyClient.TerminateConnection()