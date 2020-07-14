#include <stdio.h>
#include <stdlib.h>

#include "sv_com.h"

int rand_int(int max) {
	return rand() % max;
}

void print_recvd_packet(bcknd_to_sv_msg_t *packet) {
	printf("=========== received packet ===========\n");
	printf("function_code: %d\n", packet->function_code);
	printf("seed: %d\n", packet->seed);
	printf("mode: %d\n", packet->mode);
	printf("num_obstacles: %d\n", packet->num_obstacles);
	printf("world_size: %d\n", packet->world_size);
	printf("scale: %f\n", packet->scale);
	printf("=========================================\n");
}
