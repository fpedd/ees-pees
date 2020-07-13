#ifndef UDP_H
#define UDP_H

int udp_init();

int udp_deinit();

int udp_send(char *data, int data_len);

int udp_recv(char *buf, int buf_size);

#endif // UDP_H
