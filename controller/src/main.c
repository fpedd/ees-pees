
#include <stdio.h>

#include "udp.h"
#include "com.h"

#define PORT 6969
#define IP "127.0.0.1"

int main(int argc, char **argv) {

    (void) argc;
    (void) argv;

    udp_init();
    udp_send(argv[1], 10);
    char buf[20];
    int len = udp_recv(buf, 20);
    udp_deinit();
    
    for(int i=0; i<len; i++) {
        printf("%c", buf[i]);
    }
    printf("\n");

    return 0;
}
