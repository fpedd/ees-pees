#ifndef COM_H
#define COM_H

#define DIST_VECS    360

enum response_request {
	UNDEF = 0,                  // Invalid Packet
	COMMAND_ONLY = 1,           // Only new instructions for Robot, dont send next packet
	REQUEST_ONLY = 2,           // Only request for new packet
	COMMAND_REQUEST = 3         // New instructions for robot AND request for new packet
};
extern const char* response_request_str[];

enum direction_type {
	STEERING = 0,               // The backend commands the steering of the robot
	HEADING = 1,                // The backend commands the heading the robot should drive in
};
extern const char* direction_type_str[];

// external controller --> backend
typedef struct {
	unsigned long long msg_cnt;    // total number of messages (even) (internal)
	double time_stmp;              // time the message got send (internal)
	float sim_time;                // actual simulation time in webots
	float speed;                   // current speed of robot in webots [-1, 1]
	float actual_gps[2];           // coordiantes where the robot is
	float heading;                 // direction the front of the robot points in [-1, 1]
	float steering;                // current angle the of the steering apparatus [-1, 1]
	unsigned int touching;         // is the robot touching something?
	float distance[DIST_VECS];     // distance to the next object from robot prespective
} __attribute__((packed)) ext_to_bcknd_msg_t;

// external controller <-- backend
typedef struct {
	unsigned long long msg_cnt;    // total number of messages (odd) (internal)
	double time_stmp;              // time the message got send (internal)
	enum response_request request; // type of response the backend awaits to the packet
	enum direction_type dir_type;  // heading or steering command from backend
	float heading;                 // the direction the robot should move in next [-1, 1]
	float speed;                   // the speed the robot should drive at [-1, 1]
} __attribute__((packed)) bcknd_to_ext_msg_t;

int com_init();

int com_deinit();

float link_qualitiy(float factor);

int com_send(ext_to_bcknd_msg_t data);

int com_recv(bcknd_to_ext_msg_t *data);

#endif // COM_H
