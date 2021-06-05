//------------------------------------------------------------------
//	tcpserver.cpp
//
//	This program demonstrates the programming steps needed for 
//	creation of a network-server application (based on the TCP
//	protocol) which listens for client-programs connecting via
//	a specific port-number.  This server accepts one character
//	sent from a client, increments it, sends it back, and then 
//	closes the connection to that client and waits for another
//	until a user enters <CONTROL>-C to terminate this program. 
//
//	     compile using:  g++ tcpserver.cpp -o tctserver   
//	     execute using:  ./tcpserver
//
//	programmer: ALLAN CRUSE
//	written on: 15 JAN 2002
//	revised on: 13 APR 2008
//------------------------------------------------------------------

#include <sys/socket.h>	// for socket(), bind(), listen(), accept()
#include <netinet/in.h>	// for PF_INET, SOCK_STREAM, IPPROTO_TCP 
#include <stdio.h>	// for printf(), perror()
#include <unistd.h>	// for read(), write(), close()
#include <string.h>	// for bzero()

#define DEMO_PORT 9734

int main( void )
{
	//-----------------------------------------
	// create an unnamed socket for the server
	//-----------------------------------------
	int	sock = socket( PF_INET, SOCK_STREAM, IPPROTO_TCP );
	if ( sock < 0 )
		{
		perror( "opening stream socket" );
		return	-1;
		}
	printf( "\nsock=%d \n", sock );

	//----------------------------------------
	// construct a name for the server socket
	//----------------------------------------
	struct sockaddr_in	self;
	socklen_t		nlen = sizeof self;
	bzero( &self, sizeof self );
	self.sin_family = AF_INET;
	self.sin_port = htons( DEMO_PORT );
	self.sin_addr.s_addr = htonl( INADDR_ANY );
	if ( bind( sock, (sockaddr *)&self, nlen ) < 0 )
		{
		perror( "bind failed" );
		return	-1;
		}
	printf( "bind succeeded \n" );

	//---------------------------------------------------------
	// now create a connection queue and wait for some clients
	//---------------------------------------------------------
	if ( listen( sock, 5 ) < 0 )
		{
		perror( "listen failed" );
		return	-1;
		}		
	printf( "listen succeeded \n" );


	//---------------------------------------------------
	// main loop to process clients' connection-requests 
	//---------------------------------------------------
	while ( 1 )
		{
		sockaddr_in	peer;
		socklen_t	plen = sizeof peer;
		bzero( &peer, plen );

		printf( "server waiting \n" );

		int	client = accept( sock, (sockaddr *)&peer, &plen );
		if ( client < 0 ) { perror( "accept" ); break; }

		//---------------------------------------------
		// we can now read from or write to the client
		//---------------------------------------------
		char	ch;
		if ( read( client, &ch, 1 ) < 0 ) { perror( "read" ); break; }
		++ch;
		if ( write( client, &ch, 1 ) < 0 ) { perror( "write" ); break; }

		printf( " client data received and echoed \n" );
		close( client );
		}

	close( sock );
	printf( "\n" );
}