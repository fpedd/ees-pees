/*
* Copyright 1996-2020 Cyberbotics Ltd.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

#include <webots/robot.h>
#include <webots/supervisor.h>

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include "sv_com.h"
#include "sv_functions.h"

#define RECONNECT_WAIT_TIME_MS 4000

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


int main() {
	wb_robot_init();
	int timestep = wb_robot_get_basic_time_step();

	int connection = 1;
	int com_ret = 0;

	while(connection) {
		bcknd_to_sv_msg_t recv_buffer = {.function_code = FUNC_UNDEF};
		sv_to_bcknd_msg_t send_buffer = {.return_code = RET_UNDEF};

		sv_world_def *world = sv_simulation_init();

		 // establish coms to backend
		com_ret = sv_connect();
		if(com_ret) {
			fprintf(stderr, "SUPERVISOR: Can't connect to backend\n");
			fprintf(stderr, "SUPERVISOR: Retrying to connect...");
			usleep(RECONNECT_WAIT_TIME_MS);
			continue;
		}

		while(recv_buffer.function_code != START && com_ret != -1) {
			com_ret = sv_recv(&recv_buffer);

			print_recvd_packet(&recv_buffer);
		}

		sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.mode);
		sv_world_generate(world, recv_buffer.seed);

		send_buffer.return_code = SUCCESS;
		send_buffer.sim_time_step = timestep;
		send_buffer.target[0] = (float) world->target[0];
		send_buffer.target[1] = (float) world->target[1];

		com_ret = sv_send(send_buffer);

		sv_simulation_start(world);

		while (wb_robot_step(0) != -1 && com_ret != -1) {

			com_ret = sv_recv(&recv_buffer);

			print_recvd_packet(&recv_buffer);

			if(recv_buffer.function_code == START) {
				sv_simulation_stop();
				sv_world_clear(world);
				sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.mode);
				sv_world_generate(world, recv_buffer.seed);

				send_buffer.return_code = SUCCESS;
				send_buffer.sim_time_step = timestep;
				send_buffer.target[0] = (float) world->target[0];
				send_buffer.target[1] = (float) world->target[1];

				com_ret = sv_send(send_buffer);

				sv_simulation_start(world);
			} else if(recv_buffer.function_code == RESET) {
				sv_simulation_stop();
				sv_world_generate(world, recv_buffer.seed);

				send_buffer.return_code = SUCCESS;
				send_buffer.sim_time_step = timestep;
				send_buffer.target[0] = (float) world->target[0];
				send_buffer.target[1] = (float) world->target[1];

				com_ret = sv_send(send_buffer);

				sv_simulation_start(world);
			} else if(recv_buffer.function_code == CLOSE) {
				wb_supervisor_simulation_quit(EXIT_SUCCESS);
				connection = 0;
				break; //quit should also break the while loop
			}
		};

		sv_simulation_stop();

		if(com_ret == -1) {
			fprintf(stderr, "ERROR(supervisor_com): Trying to reconnect...");
		}
		sv_close();    //close tcp socket

		sv_world_clear(world);
		sv_simulation_cleanup(world);
	}

	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
