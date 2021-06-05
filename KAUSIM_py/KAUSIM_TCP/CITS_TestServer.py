import CITS_Server


my = CITS_Server.CITS_SERVER()

# my.SetUp()


while(1):

    enter = input("$ : ")

    if enter == '':
        print("Aborting Server !!")
        break

    else:

        try:
            
            A, B = map(int, enter.split())
            


            my.CITS_Request(A, B)

        except:
            print("Input Not Valid")
        

my.CITS_Abort()