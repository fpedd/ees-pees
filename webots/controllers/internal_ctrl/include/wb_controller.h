#ifndef WB_CONTROLLER_H
#define WB_CONTROLLER_H

#define DIST_VECS    360

// external controller --> backend
typedef struct {
    unsigned long long msg_cnt;  // total number of messages (even) (internal)
    double time_stmp;            // time the message got send (internal)
    double target_gps[3];         // coordiantes where the robot needs to go
    double actual_gps[3];         // coordiantes where the robot is
    double compass[3];            // direction the front of the robot points in
    float distance[DIST_VECS];   // distance to the next object from robot prespective
    unsigned int touching;       // is the robot touching something?
} __attribute__((packed)) to_bcknd_msg_t;

// external controller <-- backend
typedef struct {
    unsigned long long msg_cnt;  // total number of messages (odd) (internal)
    double time_stmp;            // time the message got send (internal)
    double heading;               // the direction the robot should move in next
    double speed;                 // the speed the robot should drive at
} __attribute__((packed)) from_bcknd_msg_t;


int wb_controller();

int wb_controller_test();

int wb_send(to_bcknd_msg_t data);

int wb_recv(from_bcknd_msg_t *data);


#endif //WB_CONTROLLER_H
