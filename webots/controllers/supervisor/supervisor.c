
#include <webots/robot.h>
#include <webots/supervisor.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


#include "sv_functions.h"
#include "sv_com.h"
#include "util.h"

#define RECONNECT_WAIT_TIME_S 4


int main() {

	wb_robot_init();
	int connection = 1;
	int com_ret = 0;

	while (connection) {

		bcknd_to_sv_msg_t recv_buffer = {.function_code = FUNC_UNDEF};
		sv_to_bcknd_msg_t send_buffer = {.return_code = RET_UNDEF};

		sv_world_def *world = sv_simulation_init();

		// Establish coms to backend
		com_ret = sv_connect();
		if (com_ret) {
			fprintf(stderr, "SUPERVISOR: Can't connect to backend\n");
			fprintf(stderr, "SUPERVISOR: Retrying to connect...");
			sleep(RECONNECT_WAIT_TIME_S);
			continue;
		}

		while (recv_buffer.function_code != START && com_ret != -1) {

			com_ret = sv_recv(&recv_buffer);
		}

		sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.mode);
		sv_world_generate(world, recv_buffer.seed);

		send_buffer.return_code = SUCCESS;
		send_buffer.sim_time_step = world->timestep;
		send_buffer.target[0] = (float) world->target[0];
		send_buffer.target[1] = (float) world->target[1];

		com_ret = sv_send(send_buffer);

		sv_simulation_start(world);

		while (wb_robot_step(0) != -1 && com_ret != -1) {

			com_ret = sv_recv(&recv_buffer);

			if (recv_buffer.function_code == START) {

				sv_simulation_stop();
				sv_world_clear(world);
				sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.mode);
				sv_world_generate(world, recv_buffer.seed);

				send_buffer.return_code = SUCCESS;
				send_buffer.sim_time_step = world->timestep;
				send_buffer.target[0] = (float) world->target[0];
				send_buffer.target[1] = (float) world->target[1];

				com_ret = sv_send(send_buffer);

				sv_simulation_start(world);

			} else if (recv_buffer.function_code == RESET) {

				sv_simulation_stop();
				sv_world_generate(world, recv_buffer.seed);

				send_buffer.return_code = SUCCESS;
				send_buffer.sim_time_step = world->timestep;
				send_buffer.target[0] = (float) world->target[0];
				send_buffer.target[1] = (float) world->target[1];

				com_ret = sv_send(send_buffer);

				sv_simulation_start(world);

			} else if (recv_buffer.function_code == CLOSE) {

				wb_supervisor_simulation_quit(EXIT_SUCCESS);
				connection = 0;
				break; //quit should also break the while loop TODO improve comment
			}
		};

		sv_simulation_stop();

		if (com_ret == -1) {
			fprintf(stderr, "ERROR(supervisor_com): Trying to reconnect...");
		}

		sv_close();    //close tcp socket

		sv_world_clear(world);
		sv_simulation_cleanup(world);
	}
	
	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
