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

#include "sv_com.h"
#include "sv_functions.h"

int main() {

	wb_robot_init();
	int timestep = wb_robot_get_basic_time_step();

	bcknd_to_sv_msg_t recv_buffer = {.function_code = FUNC_UNDEF};
	sv_to_bcknd_msg_t send_buffer = {.return_code = RET_UNDEF};

	sv_world_def *world = sv_simulation_init();

	 // establish coms to backend
	int ret_connect = sv_connect();
	if(ret_connect) {
		fprintf(stderr, "SUPERVISOR: Can't connect to backend\n");
	}

	while(recv_buffer.function_code != START) {
		sv_recv(&recv_buffer);
	}

	sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.fast_simulation);
	sv_world_generate(world, recv_buffer.seed);

	send_buffer.return_code = SUCCESS;
	send_buffer.sim_time_step = timestep;
	send_buffer.target[0] = world->target[0];
	send_buffer.target[1] = world->target[1];

	sv_send(send_buffer);

	sv_simulation_start(world);

	while (wb_robot_step(0) != -1) {

		sv_recv(&recv_buffer);

		if(recv_buffer.function_code == START) {
			sv_simulation_stop();
			sv_world_clear(world);
			sv_world_init(world, recv_buffer.world_size, recv_buffer.scale, recv_buffer.num_obstacles, recv_buffer.fast_simulation);
			sv_world_generate(world, recv_buffer.seed);

			send_buffer.return_code = SUCCESS;
			send_buffer.sim_time_step = timestep;
			send_buffer.target[0] = (float) world->target[0];
			send_buffer.target[1] = (float) world->target[1];

			sv_send(send_buffer);

			sv_simulation_start(world);
		} else if(recv_buffer.function_code == RESET) {
			sv_simulation_stop();
			sv_world_generate(world, recv_buffer.seed);

			send_buffer.return_code = SUCCESS;
			send_buffer.sim_time_step = timestep;
			send_buffer.target[0] = world->target[0];
			send_buffer.target[1] = world->target[1];

			sv_send(send_buffer);

			sv_simulation_start(world);
		} else if(recv_buffer.function_code == CLOSE) {
			sv_simulation_stop();
			wb_supervisor_simulation_quit(EXIT_SUCCESS);
			break; //quit should also break the while loop
		}
	};

	sv_close();

	sv_simulation_cleanup(world);

	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
