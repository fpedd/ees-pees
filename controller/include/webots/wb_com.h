#ifndef WB_COM_H
#define WB_COM_H

#define DIST_VECS 360    // Number of entries in the lidar array


// DATA FROM WEBOT
// Packet that contains all sensor data received from robot
typedef struct {
	double sim_time;              // current simulation time
	double current_speed;         // current robot speed
	double steer_angle;           // current angle the of the steering apparatus [-1, 1]
	double actual_gps[3];         // coordinates where the robot is
	double compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];    // distance to the next object from robot perspective
} __attribute__((packed)) data_from_wb_msg_t;

// COMMAND TO WEBOT
// Packet that contains the command that is send to robot
typedef struct {
	double heading;               // the direction the robot should move in next; between -1 and 1
	double speed;                 // the speed the robot should drive at; between -1 and 1
} __attribute__((packed)) cmd_to_wb_msg_t;

// INIT DATA
// Packet that contains some constant data from the robot/world configuration
typedef struct {
	int timestep;             // timestep length (in ms) of the simulation
	double maxspeed;          // maximum rotational speed of the robots drive axle
	double lidar_min_range;   // minimum detection range of lidar. Obstacles closer will be shown at max range
	double lidar_max_range;   // maximum detection range of lidar
}__attribute__((packed)) init_to_ext_msg_t;


void wb_init_com();

int wb_send(cmd_to_wb_msg_t data);

int wb_recv_init(init_to_ext_msg_t *data);

int wb_recv(data_from_wb_msg_t *data);

void wb_test_com();


#endif // WB_COM_H
