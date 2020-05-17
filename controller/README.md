# EES-PEES Robot Project Controller

## Architecture
The code is split up into two directories:
* `include/`, headers that define the interface of every source file
* `src/`, the source files, including the main entry point `main.c`

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
## Protocol

* IP `127.0.0.1` (local host)
* Controller Port `6969`
* Backend Port `6970`

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
#define DIST_VECS    360

// external controller --> backend
typedef struct {
	unsigned long long msg_cnt;  // total number of messages (even) (internal)
	double time_stmp;            // time the message got send (internal)
	float target_gps[3];         // coordiantes where the robot needs to go
	float actual_gps[3];         // coordiantes where the robot is
	float compass[3];            // direction the front of the robot points in
	float distance[DIST_VECS];   // distance to the next object from robot prespective
	unsigned int touching;       // is the robot touching something?
	} __attribute__((packed)) to_bcknd_msg_t;

	// external controller <-- backend
	typedef struct {
		unsigned long long msg_cnt;  // total number of messages (odd) (internal)
		double time_stmp;            // time the message got send (internal)
		float heading;               // the direction the robot should move in next
		float speed;                 // the speed the robot should drive at
	} __attribute__((packed)) from_bcknd_msg_t;
```

Variables inside the messages with `(internal)` next to them should never be written
by the application. These get filled the transmission protocol. They can however, be read.

Explanation of `to_bcknd_msg_t`:
* `unsigned long long msg_cnt` is a running count of all transmitted messages between
  controller and backend. They start at 0. The first message, that will establish the
  communication, is send with `msg_cnt` as 0. It gets send by the external controller.
  The backend will then respond with the first message from the backend to the
  external controller with `msg_cnt` set to 1. The external controller should
  only ever send even numbers, the backend only odd numbers.
* `double time_stmp` is the local system time in seconds (with nanosecond precision)
  since 1970. It gets set as the last variable, just before the message gets send out.
* `float target_gps[3]` are the latitude, longitude and altitude (in meters) coordinates
  the robot has to reach in order to complete the mission.
* `float actual_gps[3]` are the coordinates the robot is currently at.
  It is in the same format as the `target_gps`.
* `float compass[3]` the direction the front of the robot is currently pointing
  at in 3d space relative to the global north in degree.  
* `float distance[DIST_VECS]` the distance (in meters) to the next solid object
  with the direction corresponding to the index of the array. So if distance[66]
  = 1.23, the distance to the next solid object in direction 66 degree is 1.23 meters.
  The the maximum range of the lidar is about 3.5 meters. All values bigger than
  that have to be assumed to be invalid. We will try to set invalid entries to 69 meters.
* `unsigned int touching` is set to the number of objects the robot is currently
  touching / colliding with.

Explanation of `from_bcknd_msg_t`:
* `unsigned long long msg_cnt` see above.
* `double time_stmp` see above.
* `float heading` the direction the robot should go move in next (degree, relative
  to the global north in the horizontal plane).
* `float speed` the speed the robot should move at, 0 if it should stop (in m/s).
