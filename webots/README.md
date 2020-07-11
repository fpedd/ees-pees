# EES-PEES Robot Project: Webots Environment

The Webots simulator is the basis of the project as it is where the virtual robot is navigating to a target.
To understand how the Webots environment is controlled using network connections, have a look at their interface.

## Interface

### Internal controller

The internal controller (webots side) is used to control the robot and get sensed data, this means it translates arriving packets to webots API calls for the actuators and also to retrieve sensordata to send it.
On the network side it actively connects to the external controller via TCP on startup and communicates using the following types of packets.

#### Packet structure

An excerpt from the "internal_com.h" of the internal controller:
```c
// webot --> external controller
typedef struct {
	double sim_time;              // current simulation time [if requested]
	double current_speed;         // current robot speed [if requested]
	double actual_gps[3];         // coordiantes where the robot is
	double compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];    // distance to the next object from robot prespective
	double steer_angle;           // current measured steering angle
} __attribute__((packed)) wb_to_ext_msg_t;

// webot <-- external controller
typedef struct {
	double heading;               // the direction the robot should move in next; between -1 and 1
	double speed;                 // the speed the robot should drive at; between -1 and 1
} __attribute__((packed)) ext_to_wb_msg_t;

// init msg --> external controller
typedef struct {
	int timestep;             // timestep (in ms) of the simulation
	double maxspeed;          // maximum speed of the Robot in m/s
	double lidar_min_range;   // minimum detection range of lidar. Obstacles closer will be shown at max range
	double lidar_max_range;   // maximum detection range of lidar
}__attribute__((packed)) init_to_ext_msg_t;
```

The init message is sent once after connection establishment.

### Supervisor (SV) controller

The supervisor controller (webots side) is designed to make automated training of the robot possible. To counteract overfitting of the neural network the supervisor controller is capable of generating a world. Given size, scale and the amount of obstacles, an imaginary grid is randomly filled with these obstacles to create a world through which the robot is challenged to navigate.
On the network side it actively connects to the backend via TCP on startup and retries to connect every 4 seconds if connection is lost.
**Important** Using the supervisor controller for other worlds than "training_env.wbt" need the same DEFs for proper function as well as the attributes of the *supervisor* robot set SYNCHRONIZATION to false and SUPERVISOR to true.
To use the supervisors asserts, use the debugging flag when compiling.

#### Packet structure

An excerpt from the "sv_com.h" of the supervisor controller:
```c
enum function_code {
	FUNC_UNDEF = -1,
    NO_FUNCTION = 0,
    START = 1,
    RESET = 2,
    CLOSE = 3
};

enum return_code {
    RET_UNDEF = -1,
    SUCCESS = 0,
    ERROR = 1
};

// supervisor --> backend
typedef struct {
	enum return_code return_code;   // return_code [enum return_code]
	int sim_time_step;              // simulation time_step in ms [int]
	float target[2];                // target position [float[2]]
} __attribute__((packed)) sv_to_bcknd_msg_t;

// supervisor <-- backend
typedef struct {
	enum function_code function_code; // function code [enum function_code]
	int seed;                         // seed [int]
	enum sv_sim_mode mode;            // fast_simulation [enum sv_sim_mode]
	int num_obstacles;                // num_obstacles [int]
	int world_size;                   // world_size in blocks [int]
	float scale;                      // scale of the world, actual_size = world_size*scale [float]
} __attribute__((packed)) bcknd_to_sv_msg_t;
```

The function code defines the interpretation of the package. "Start" creates a world with all given parameters. "Reset" on the other hand is used for optimization purposes, as it only creates a new world based on the parameters of the last start packet but with a new seed from the reset. As this reduces time usage significantly it is very useful for the usual batch/epoch training sessions.
Target is sent back as both start and target are set by the supervisor.