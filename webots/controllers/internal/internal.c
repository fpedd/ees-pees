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

#include <webots/device.h>
#include <webots/led.h>
#include <webots/motor.h>
#include <webots/robot.h>
#include <webots/lidar.h>
#include <webots/gps.h>
#include <webots/compass.h>
#include <webots/position_sensor.h>

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "internal_com.h"
#include "util.h"



int main(int argc, char **argv) {

	wb_robot_init();

	const int timestep = (int)wb_robot_get_basic_time_step();

	printf("This C controller is an TCP interface to Webots\n\n");

	WbDeviceTag motor, steer, angle, lidar, gps, compass;
	motor   = wb_robot_get_device("motor");
	steer   = wb_robot_get_device("pivot");
	angle   = wb_robot_get_device("pivot sensor");
	lidar   = wb_robot_get_device("lidar");
	gps     = wb_robot_get_device("gps");
	compass = wb_robot_get_device("compass");

	// configure devices
	// Switch to velocity control mode for unbounded motors.
	wb_motor_set_position(motor, INFINITY);
	wb_lidar_enable(lidar, timestep);
	wb_lidar_disable_point_cloud(lidar);
	wb_gps_enable(gps, timestep);
	wb_compass_enable(compass, timestep);
	wb_position_sensor_enable(angle, timestep);

	/*
	// Print lidar properties
	printf("Frequency: %f\n", wb_lidar_get_frequency(lidar));
	printf("MAXFreq: %f\n", wb_lidar_get_max_frequency(lidar));
	printf("MINFreq: %f\n", wb_lidar_get_min_frequency(lidar));
	printf("FOV: %f\n", wb_lidar_get_fov(lidar));
	printf("MAXRange: %f\n", wb_lidar_get_max_range(lidar));
	printf("MINRange: %f\n", wb_lidar_get_min_range(lidar));
	printf("Resolution: %i\n", wb_lidar_get_horizontal_resolution(lidar));
	printf("SamplPer: %i\n", wb_lidar_get_sampling_period(lidar));
	*/

	int res = wb_lidar_get_horizontal_resolution(lidar);
	printf("lidar resolution %i\n", res);

	printf("Starting Coms on Webots Controller\n");
	int ret_connect = internal_connect();
	if (ret_connect) {
		printf("INTERNAL: Can't establish connection to ext controller\n");

		// TODO: stand and wait to connect again?

		wb_robot_cleanup();
		return EXIT_SUCCESS;
	}

	wb_robot_step(0);

	// Send init information
	init_to_ext_msg_t init_data;
	init_data.timestep = timestep;
	init_data.maxspeed = wb_motor_get_max_velocity(motor);
	init_data.lidar_min_range = wb_lidar_get_min_range(lidar);
	init_data.lidar_max_range = wb_lidar_get_max_range(lidar);

	internal_send_init(init_data);


	// Loop until the simulator stops the controller.
	while (wb_robot_step(timestep) != -1) {

		wb_to_ext_msg_t robot_data;
		memset(&robot_data, 0, sizeof(wb_to_ext_msg_t));

		// read values from devices
		robot_data.sim_time = wb_robot_get_time();
		robot_data.current_speed = wb_gps_get_speed(gps);
		robot_data.steer_angle = wb_position_sensor_get_value(angle);
		memcpy (&robot_data.actual_gps, wb_gps_get_values(gps), sizeof(double) * 3);
		memcpy (&robot_data.compass, wb_compass_get_values(compass), sizeof(double) * 3);
		memcpy (&robot_data.distance, wb_lidar_get_range_image(lidar), sizeof(float) * DIST_VECS);

		// print_wb_to_ext(robot_data);


		// send data
		// printf("Sending test_msg on Webots Controller\n");
		internal_send(robot_data);

		// receive response
		ext_to_wb_msg_t buf;
		memset(&buf, 0, sizeof(ext_to_wb_msg_t));

		// printf("receiving Message on Webots Controller\n");
		internal_recv(&buf);

		// printf("===========RECEIVED=========\n");
		// printf("Steering:    %f\n", buf.heading);
		// printf("Motor Speed: %f\n", buf.speed);
		// printf("============================\n");

		// Set motor speed and steering
		wb_motor_set_position(steer, buf.heading);
		wb_motor_set_velocity(motor, buf.speed);

	}

	wb_robot_cleanup();

	return EXIT_SUCCESS;
}
