# EES-PEES Robot Project Webots

This is where all code for the webots controller stuff will go. Please use
this readme file to document the architecture.

INTERFACE

// webot --> external controller
typedef struct {  
    unsigned long long msg_cnt;  // total number of messages (even) (internal)        NOT USED
    double time_stmp;            // time the message got send (internal)              NOT USED
    double target_gps[3];         // coordiantes where the robot needs to go
    double actual_gps[3];         // coordiantes where the robot is
    double compass[3];            // direction the front of the robot points in
    float distance[DIST_VECS];   // distance to the next object from robot prespective
    unsigned int touching;       // is the robot touching something?                  NOT USED
} __attribute__((packed)) to_bcknd_msg_t;

// webot <-- external controller
typedef struct {
    unsigned long long msg_cnt;  // total number of messages (odd) (internal)       NOT USED
    double time_stmp;            // time the message got send (internal)            NOT USED
    double heading;               // the direction the robot should move in next    Should be value between -1 and 1
    double speed;                 // the speed the robot should drive at            Should be value between -1 and 1
} __attribute__((packed)) from_bcknd_msg_t;
