#ifndef COM_H
#define COM_H

#define DIST_VECS    360

// external controller --> backend
typedef struct {
	unsigned long long msg_cnt;  // total number of messages (even) (internal)
	double time_stmp;            // time the message got send (internal)
	float sim_time;              // actual simulation time in webots
	float speed;                 // current speed of robot in webots
	float actual_gps[2];         // coordiantes where the robot is
	float heading;               // direction the front of the robot points in
	unsigned int touching;       // is the robot touching something?
	float distance[DIST_VECS];   // distance to the next object from robot prespective
} __attribute__((packed)) ext_to_bcknd_msg_t;

// external controller <-- backend
typedef struct {
	unsigned long long msg_cnt;  // total number of messages (odd) (internal)
	double time_stmp;            // time the message got send (internal)
	float heading;               // the direction the robot should move in next
	float speed;                 // the speed the robot should drive at
} __attribute__((packed)) bcknd_to_ext_msg_t;

int com_init();

int com_send(ext_to_bcknd_msg_t data);

int com_recv(bcknd_to_ext_msg_t *data);

#endif // COM_H
