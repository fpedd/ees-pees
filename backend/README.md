# EES-PEES Robot Project Backend    

## Webots environment
* Goal: create a openai-gym-wrapper around the communication to Webots (http://gym.openai.com/docs/)
* `import environment`
* load environment by `env = environment.WebotsEnv()`
* Main arguments:
    * `seed`, used to setup different Webot environments in **training** in combination with the supervisor mode
    * `action_class`, used to setup the **action_space** and the mapping of the actions to webots actions via **map()**. For example: `action_class=DiscreteAction(directions=3, speeds=3, mode="flatten")` will setup a discrete Action space of size 9. Possile actions to be calculated by an agent (e.g. openai model) are 0:8. **map()** is used to translate the action index to a webot action. Example 0: decrease speed, turn left. For more information of the mapping see *DiscreteAction* in **Action.py**. Another possiblity is `action_class=ContinuousAction`, this will set the **action_space=[-1, 1]^2** with a direct mapping.
    * `reward_class`, uses the environment information to calculate a reward for the *last action* resulting in the *current state*. For different reward options see **Reward.py**.
    * `observation_func`, used the environment to setup an observation to be fed to some agent. Not final yet, probably will change to class to set observation_space simultaneously.
* make a action step by `state, reward, done, {} = env.step(action)`. Gets the current state from the external controller and sends action back.
* To get the information of the communication, call appropriate action on `env.com`

## Current configurations - Config.py
    # ----------------------------------------------------------------------
    # external controller protocol
    IP = "127.0.0.1"
    CONTROL_PORT = 6969
    BACKEND_PORT = 6970
    PACKET_SIZE = 1480
    TIME_OFFSET_ALLOWED = 1.0
    DIST_VECS = 360

    # ----------------------------------------------------------------------
    # supervisor communication protocol
    IP_S = "127.0.0.1"
    PORT_S = 10201
    PACKET_SIZE_S = 16

    # settable for environment start via supervisor
    fast_simulation = False
    num_obstacles = 10
    world_size = 10
    seed = None

    # (received) world metadata
    gps_target = None
    sim_time_step = 32  # ms

## Interface for automated testing - automate.py
```
// supervisor --> backend
typedef struct {
	int return_code;         // return_code [int]
	int sim_time_step;       // simulation time_step in ms [int]
	float target[2];         // target gps [float]
} __attribute__((packed)) sv_to_bcknd_msg_t;

// supervisor <-- backend
typedef struct {
	int function_code;    // function code [int]
	int seed;             // seed [int]
	int fast_simulation;  // fast_simulation [int]
	int num_obstacles;    // num_obstacles [int]
	int world_size;       // world_size in meter [int]
} __attribute__((packed)) bcknd_to_sv_msg_t;
```

## Interface to external controller - communicate.py
* `Packet` - holds the received data in `buffer` as well as some control information `time`, `count` and `success` (the packet has arrived as intented from the external controller.
* `Com` - Main communication class, used to receive (`recv()`) and `send(action:WebotAction)` data from the external controller.

## webot.py
* `WebotState` - holds all information about the current state of the Webot, i.e. `gps_target`, `gps_actual`, `compass`, `distance`, `touching`. State will be filled from `Packet.buffer` using internal function `fill_from_buffer(buffer).` To get the current state as numpy.ndarray call `get()`.
* `WebotAction` - blueprint for Webots actions to be used in other modules. Attributes: `heading`, `speed`.

<!-- ## Fake environment - environment.py
* `import environment`
* There are currenty 3 fake environments available: `FakeEnvironmentMini` (Gridsize: 10x10), `FakeEnvironmentMedium` (50x50) and `FakeEnvironmentLarge` (100x100). To import them use for example: `env = environment.FakeEnvironmentMedium()`.
* Each environment takes *optional* 2 arguments: (1) `num_of_sensors` - in how many evenly spaces directions should the lidar return values, should be a multiple of 4 and (2) `obstacles_each` - how many random obstacles should be placed horizontally AND vertically. Maze could be unsolvable. **The possible directions the roboter can take always equals `num_of_sensors`**.
* To **plot** the current environment with obstacles, target and robotor call `env.render()`.
* The next **step** is performed via `env.step(action)`. The argument `action` must be of the form (`orientation_id`, `step_len`). `orientation_id` describes the direction the roboter should take. (e.g for `num_of_sensors=4`, 0:E, 1:S, 2:W, 3:N. For`num_of_sensors=8` it becomes 0:E, 1:SE, 2:S ,..., 6:N, 7:NE). `step_len` describes roughly how many steps of the grid to take. The `step()` function returns `state, reward, done, {}` as in openai Gym. `state` is a numpy array with `[pos[0], pos[1], target[0], target[1], distance0, distance1, .. distanceN-1]`. -->
