#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <arpa/inet.h>  /* definition of inet_ntoa */
#include <netdb.h>      /* definition of gethostbyname */
#include <netinet/in.h> /* definition of struct sockaddr_in */
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h> /* definition of close */

#include <webots/motor.h>
#include <webots/robot.h>

#include "tcp.h"
#include "wb_controller.h"
#include "util.h"



int wb_controller(){

	wb_robot_init();

	// get timestep from world info
	const int timestep = (int) wb_robot_get_basic_time_step();

	//enable devices
	WbDeviceTag lidar = wb_robot_get_device("LDS-01");
	WbDeviceTag gps = wb_robot_get_device("gps");
	WbDeviceTag compass = wb_robot_get_device("compass");

	wb_lidar_enable (lidar, timestep);
	wb_gps_enable (gps, timestep);
	wb_compass_enable (compass, timestep);

	//connect to external controller
	printf("Starting Coms on Webots Controller\n");
	tcp_connect();

	//run
	while (wb_robot_step(timestep) != -1) {

		to_bcknd_msg_t robot_data;
		memset(&robot_data, 0, sizeof(to_bcknd_msg_t));


		//get sensor data
		robot_data.time_stmp = wb_robot_get_time();
		// robot_data.speed = wb_gps_get_speed(gps);
		robot_data.actual_gps = wb_gps_get_values(gps);
		robot_data.compass = wb_compass_get_values(compass);
		robot_data.distance = wb_lidar_get_range_image(lidar);

		printf("Sending test_msg on Webots Controller\n");
		wb_send(robot_data);

		from_bcknd_msg_t buf;
		memset(&buf, 0, sizeof(from_bcknd_msg_t));

		printf("receiving Message on Webots Controller\n");

		wb_recv(&buf);

		printf("===========RECEIVED=========\n");
		printf("Heading: %f\n", test_buf.heading);
		printf("Speed: %f\n", test_buf.speed);
		printf("============================\n");

	}



	wb_robot_cleanup();

	return 0;
}



int wb_controller_test(){

	printf("Starting Coms on Webots Controller\n");
	tcp_connect();

	from_bcknd_msg_t test_buf;
	memset(&test_buf, 0, sizeof(from_bcknd_msg_t));

	printf("receiving test_msg on Webots Controller\n");
	wb_recv(&test_buf);

	printf("===========RECEIVED=========\n");
	printf("Heading: %f\n", test_buf.heading);
	printf("Speed: %f\n", test_buf.speed);
	printf("============================\n");

	to_bcknd_msg_t test_msg;
	memset(&test_msg, 0, sizeof(to_bcknd_msg_t));

	test_msg.target_gps[0] = 5.55;
	test_msg.target_gps[1] = 6.66;
	test_msg.target_gps[2] = 7.77;


	printf("Sending test_msg on Webots Controller\n");
	wb_send(test_msg);

	return 0;
}

int wb_send(to_bcknd_msg_t data) {

	data.msg_cnt = 0;
	data.time_stmp = 0;

    int len = tcp_send((char *) &data, sizeof(to_bcknd_msg_t));
	if (len < (int) sizeof(to_bcknd_msg_t)) {
		error("wb_send: Did not send complete struct");
	}

    return 0;
}

int wb_recv(from_bcknd_msg_t *data) {

	memset(data, 0, sizeof(from_bcknd_msg_t));

    int len = tcp_recv((char *)data, sizeof(from_bcknd_msg_t));
    if (len < (int) sizeof(from_bcknd_msg_t)) {
        error("wb_recv: did not receive complete data");
    }

    return 0;
}
