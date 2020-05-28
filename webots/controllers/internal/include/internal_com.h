#ifndef INTERNAL_COM_H
#define INTERNAL_COM_H

#define DIST_VECS    360

// webot --> external controller
typedef struct {
	double sim_time;                 // current simulation time [if requested]
	double current_speed;               // current robot speed [if requested]
	double actual_gps[3];         // coordiantes where the robot is
	double compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];    // distance to the next object from robot prespective
} __attribute__((packed)) wb_to_ext_msg_t;

// webot <-- external controller
typedef struct {
	double heading;               // the direction the robot should move in next; between -1 and 1
	double speed;                 // the speed the robot should drive at; between -1 and 1
} __attribute__((packed)) ext_to_wb_msg_t;

int internal_connect();

int internal_send(wb_to_ext_msg_t data);

int internal_recv(ext_to_wb_msg_t *data);


#endif //INTERNAL_COM_H
