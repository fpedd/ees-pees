#ifndef INTERNAL_COM_H
#define INTERNAL_COM_H

// Number of lidar distance vectors
#define DIST_VECS 360

// webot --> external controller
typedef struct {
	double sim_time;           // current simulation time (in seconds)
	double current_speed;      // current absolute robot speed (in m/s)
	double steer_angle;        // currently measured steering angle (in rad)
	double actual_gps[3];      // coordinates where the robot is (in m)
	double compass[3];         // direction the front of the robot points to
	float distance[DIST_VECS]; // distance to the next object from robot perspective (in m)
} __attribute__((packed)) wb_to_ext_msg_t;

// webot <-- external controller
typedef struct {
	double heading;            // the direction the robot should move in next, between -1 and 1
	double speed;              // the speed the robot should drive at, between -22 (forwards) and 22 (backwards)
} __attribute__((packed)) ext_to_wb_msg_t;

// init msg --> external controller
typedef struct {
	int timestep;              // timestep length of the simulation (in ms)
	double maxspeed;           // maximum rotational speed of the robots drive axle
	double lidar_min_range;    // minimum detection range of lidar. Obstacles closer will be shown at max range
	double lidar_max_range;    // maximum detection range of lidar
}__attribute__((packed)) init_to_ext_msg_t;

int internal_connect();

int internal_send_init(init_to_ext_msg_t data);

int internal_send(wb_to_ext_msg_t data);

int internal_recv(ext_to_wb_msg_t *data);


#endif //INTERNAL_COM_H
