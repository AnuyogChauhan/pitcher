
#include <arpa/inet.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>
#include <oscpack/osc/OscOutboundPacketStream.h>
#include <oscpack/ip/UdpSocket.h>

#define SERVER "127.0.0.1"
#define PORT 6999 //The port on which to send data

int currentX = 0;
int currentY = 0;

void sig_handler( int signo ){
  if( signo == SIGUSR1){
      currentX = 0;
      currentY = 0;
  }
}

int main(int argc, char** argv)
{
    int fd, bytes;
    unsigned char data[3];

    const char *pDevice = "/dev/input/mice";
    
    
    int xMax = 1024;
    int yMax = 768;


    if( signal(SIGUSR1, sig_handler) == SIG_ERR ){
      printf("\n can't catch SIGUSR1\n");
    }

    // Open Mouse
    fd = open(pDevice, O_RDWR);
    if(fd == -1)
    {
        printf("ERROR Opening %s\n", pDevice);
        return -1;
    }

    int left, middle, right;
    signed char x, y;
    char buffer[1024];
    
    UdpTransmitSocket transmitSocket( IpEndpointName( SERVER, PORT ) );

    while(1)
    {
        // Read Mouse     
        bytes = read(fd, data, sizeof(data));

        if(bytes > 0)
        {
            left = data[0] & 0x1;
            right = data[0] & 0x2;
            middle = data[0] & 0x4;

            x = data[1];
            y = data[2];
            
            currentX += (int)x;
            currentY += (int)y;
            
            if( currentX > xMax )
                currentX = xMax - 1;
            
            if( currentY > yMax )
                currentY = yMax - 1;
                
            if( currentX < 0 )
                currentX = 0;
                
            if( currentY < 0 )
                currentY = 0;
            
            
            

            float xf = ((float)currentX)/((float)xMax);
            float yf = 1.0f - ((float)currentY)/((float)yMax);
            bool mouseClick = ((int)left) == 1; 

            //printf("x=%f, y=%f, left=%d, middle=%d, right=%d\n", xf, yf, left, middle, right);
            

            osc::OutboundPacketStream p( buffer, 1024 );

            if(mouseClick){
                p << osc::BeginMessage( "/mouse" ) << xf << yf << 1 << osc::EndMessage;
                p << osc::BeginMessage( "/mouse" ) << xf << yf << mouseClick << osc::EndMessage;
            }else{
                p << osc::BeginMessage( "/mouse" ) << xf << yf << 0 << osc::EndMessage;
                p << osc::BeginMessage( "/mouse" ) << xf << yf << mouseClick << osc::EndMessage;
            }
            
            transmitSocket.Send( p.Data(), p.Size() );
        } 
          
    }
    return 0; 
}
