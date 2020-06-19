#ifndef WB_COM_H
#define WB_COM_H

#define DIST_VECS    360

// webot --> external controller
typedef struct {
	double sim_time;              // current simulation time
	double current_speed;         // current robot speed
	double actual_gps[3];         // coordiantes where the robot is
	double compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];    // distance to the next object from robot prespective
} __attribute__((packed)) data_from_wb_msg_t;

// webot <-- external controller
typedef struct {
	double heading;               // the direction the robot should move in next; between -1 and 1
	double speed;                 // the speed the robot should drive at; between -1 and 1
} __attribute__((packed)) cmd_to_wb_msg_t;

// init msg --> external controller
typedef struct {
	int timestep;             // timestep (in ms) of the simulation
	double maxspeed;          // maximum speed of the Robot in m/s
	double lidar_min_range;   // minimum detection range of lidar. Obstacles closer will be shown at max range
	double lidar_max_range;   // maximum detection range of lidar
}__attribute__((packed)) init_to_ext_msg_t;

void wb_init_com();

int wb_send(cmd_to_wb_msg_t data);

int wb_recv_init(init_to_ext_msg_t *data);

int wb_recv(data_from_wb_msg_t *data);

void wb_test_com();


#endif // WB_COM_H
