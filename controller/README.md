# EES-PEES Robot Project Controller

## Architecture
The code is split up into two directories:
* `include/`, headers that define the interface of every source file
* `src/`, the source files, including the main entry point `main.c`

It is further split into a `webots` directory controlling the communication and logic with the webot and the `backend` directory that handles communication with the backend.

We also have a `Makefile` to compile the code in the root directory.

## Usage
Use the `Makefile` in the root directory to compile the code. If there are no erros,
a new `build` directory will be created. The build directory is not part of
the version control system and should not be added or commited via git
(we have `/build` added to our) `.gitignore`. You can then execute the binary in the
`/build` directory.

```
make
./build/controller
```

To get a clean start (delete all build files):

```
make clean
```

## General functioning
The external controller consists of two parallely running threads, the webot_worker and the backend_worker. Both of them communicate by using externally defined message structs that are blocked from simultaneous access by mutexes. The general idea is, that the webot_worker receives sensor data from the webot, reformats it to the format the backend needs and puts it into the corresponding struct for the backend_worker to read it. Then it continues to read the values the backend_worker left for it and uses it to do safety logic (TODO), and calculate the new motor controll settings for the webot using a PID controller. Then it sends the new commands to the webot.
At the same time the backend_worker waits for the backend to either request the newest sensor data, or sending updated speed and heading or both.
The frequency at which both threads perform their work-loops is no yet controlled or synchronized.


## Testing
We are using [Google Test](https://github.com/google/googletest) to run unit tests on our code. Before you will be able to run any tests you will need to install Google Test on your machine. Please follow the installation instructions [here](https://www.eriksmistad.no/getting-started-with-google-test-on-ubuntu/) to install Google Test. After that you will be able to call `make test`. That will compile and run all unit tests. You can add your own unit tests in the `/test` directory. You may need to create a new corresponding test file in that directory if there is none already. The tests will also be automatically executed when pushing to Github using [Github Actions](https://help.github.com/en/actions).

## Protocol

* IP `127.0.0.1` (local host)
* Controller Port `6969`
* Backend Port `6970`
* Webot Port `10200`

### Frontend
The communication with the Webot uses a TCP connection. There are three different packages that can be send on this connection:
* init messages that are send once at the startup of the internal controller to the external controller
* webot --> external controller messages that consist of the current sensor data the robot sends every timestep
* webot <-- external controller messages that consist of the speed and heading the robot should configure its motors to

###### init msg --> external controller
```
typedef struct {
	int timestep;             // timestep (in ms) of the simulation
	double maxspeed;          // maximum speed of the Robot in m/s
	double lidar_min_range;   // minimum detection range of lidar. Obstacles closer will be shown at max range
	double lidar_max_range;   // maximum detection range of lidar
	double target_gps[3];     // coodinates of the target
}__attribute__((packed)) init_to_ext_msg_t;
```
* timestep is the realtime (in ms) that passes in the simulation with each simulated step. It is defined by the webots world. Sensor data does not change in intervalls smaller than this.
* maxspeed defines the maximum speed the robot motor can drive at. This is used solely to scale the used speeds to a intervall from -1 to 1.
* lidar min and max range are the ranges in which the lidar detects obstacles. Values below or above this are reported at the lidar_max_range value. These values are subject to noise and can differentiate slightly from the max value though
* (TODO) target_gps is not yet inplemented.

###### webot --> external controller
```
typedef struct {
	double sim_time;              // current simulation time [if requested]
	double current_speed;         // current robot speed [if requested]
	double actual_gps[3];         // coordiantes where the robot is
	double compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];    // distance to the next object from robot prespective
} __attribute__((packed)) wb_to_ext_msg_t;
```
* sim_time is the current time (in ms) starting at 0 when the simulation starts.
* current_speed is the robots current speed (in m/s) measured by the gps
* compass gives back a 3D vector pointing in the direction the robot points. This is used to calculate the heading of the robot and whether or not it is upright (TODO).
* distance is the data from the lidar sensor where the first entry is in front of the robot and the following entries are in clockwise direction

###### webot <-- external controller
```
typedef struct {
	double heading;               // the direction the robot should move in next
	double speed;                 // the speed the robot should drive at
} __attribute__((packed)) ext_to_wb_msg_t;
```
* the heading value tells the robot at which angle it positions its back axle. It _can_ range from 0 to 1 but should be between 0,25 and 0,75 to avoid clipping. 0,5 is used to drive straight
* speed gives the webots motor a value. It should be between -max_speed and +max_speed. Negative numbers mean the robot is driving forwards (ONLY INTERNALLY, values from backend should have the more intuitive positive=forward format)


### Backend

The protocol should (for now) run over UDP. UDP has a checksum build in. So if a
packet arrives, it is intact. On top of that we have to ensure that:
* when we have no packet / communication for a certain time we will timeout and
  go into a failsafe state
* that packets arrive in order, so old packets get discarded
* check how much delay we have on the line and handle that accordingly

The main idea is, that we have to types of messages. One that gets transmitted from
the external controller to the backend and one that get transmitted from the backend
to the external controller. They currently look like this:

```
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
	unsigned int action_denied;    // did we have to take over control for saftey reasons
	unsigned int discr_act_done;   // did the robot complete its discrete action
	float distance[DIST_VECS];     // distance to the next object from robot prespective
} __attribute__((packed)) ext_to_bcknd_msg_t;

// external controller <-- backend
typedef struct {
	unsigned long long msg_cnt;    // total number of messages (odd) (internal)
	double time_stmp;              // time the message got send (internal)
	enum response_request request; // type of response the backend awaits to the packet
	enum discrete_move move;       // ignore everything else and do a discrete_action
	enum direction_type dir_type;  // heading or steering command from backend
	float heading;                 // the direction the robot should move in next [-1, 1]
	float speed;                   // the speed the robot should drive at [-1, 1]
} __attribute__((packed)) bcknd_to_ext_msg_t;
```

Variables inside the messages with `(internal)` next to them should never be written
by the application. These get filled by the transmission protocol. They can however, be read.

Explanation of `to_bcknd_msg_t`:
* `unsigned long long msg_cnt` is a running count of all transmitted messages between
  controller and backend. They start at 0. The first message, that will establish the
  communication, is send with `msg_cnt` as 0. It gets send by the external controller.
  The backend will then respond with the first message from the backend to the
  external controller with `msg_cnt` set to 1. The external controller should
  only ever send even numbers, the backend only odd numbers.
* `double time_stmp` is the local system time in seconds (with nanosecond precision)
  since 1970. It gets set as the last variable, just before the message gets send out.
* `float sim_time` Actual simulation time in webots in ms.
* `float speed` Current speed of robot in webots [-1, 1].
* `float actual_gps[2]` are the coordinates the robot is currently at.
  It is in the same format as the `target_gps`.
* `float heading` the direction the front of the robot is currently pointing at [-1, 1].  
* `float steering` current angle the of the steering apparatus that the robot uses to steer [-1, 1].
* `unsigned int touching` is set to the number of objects the robot is currently
touching / colliding with.
* `unsigned int action_denied` is set if the external controller needed to take
  over control because backend action was not safe.
* `unsigned int discr_act_done` is set when the requested discrete action is done.
* `float distance[DIST_VECS]` the distance (in meters) to the next solid object
  with the direction corresponding to the index of the array. So if distance[66]
  = 1.23, the distance to the next solid object in direction 66 degree is 1.23 meters.
  The the maximum range of the lidar is about 3.5 meters. All values bigger than
  that have to be assumed to be invalid. We will try to set invalid entries to 69 meters.

Explanation of `from_bcknd_msg_t`:
* `unsigned long long msg_cnt` More info see above.
* `double time_stmp` More info see above.
* `enum response_request request` type of response the backend expects. More info see below.
* `enum discrete_move move; ` if this is set to a non zero value the heading and speed
  are ignored and a discrete action according to the move number is taken. if the action is
  done, the `discr_act_done` variable is set.
* `enum direction_type dir_type` heading or steering command from backend. More info see below.
* `float heading` the direction the robot should go move in next [-1, 1] (relative
  to the global north in the horizontal plane).
* `float speed` the speed the robot should move at, 0 if it should stop [-1, 1].

```
enum response_request {
	UNDEF = 0,                  // Invalid Packet
	COMMAND_ONLY = 1,           // Only new instructions for Robot, dont send next packet
	REQUEST_ONLY = 2,           // Only request for new packet
	COMMAND_REQUEST = 3         // New instructions for robot AND request for new packet
};
```

Explanation of `enum response_request`:
* `UNDEF`: Invalid Packet. Wait for next message from backend
* `COMMAND_ONLY`: Only forward heading and speed to `webot_worker`, then wait for next message from backend
* `REQUEST_ONLY`: Only send newest sensordata from `webot_worker` to backend, then wait for next message from backend
* `COMMAND_REQUEST`: Do both of the above, then wait for next message from backend

```
enum direction_type {
	STEERING = 0,               // The backend commands the steering of the robot
	HEADING = 1,                // The backend commands the heading the robot should drive in
};
```

Explanation of `enum direction_type`:
* `STEERING`: The backend commands the robot to move its sterring aparatus in a certain way.
  The backend steers the robot itself. No help from any PID controller or so.
* `HEADING`: The backend commands the robot to move in a ceratin direction.
  The robot then uses controllers to ensure that it is going in that direction.
