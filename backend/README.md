# EES-PEES Robot Project Backend

## Overview
* fakegym -> code and notebooks to train and run a RL agent on our self created fake environment
* research -> old notebooks with our first attempts to create RL agents
* test -> unit and integration tests for the webots environment and fake environments
* webotsgym -> heart of the backend with code to train and run a RL agent on the webots environment
* james.py -> wrapper class to control the robot on your own in the webots environment

For insights into the fake environment, research or the test please see the readme for the specific areas in the regarding folder.
In the following you can find a closer view on the functionalities of the webotsgym and what is possible from a more technical perspective. 

## Webotsgym
* Goal: create a openai-gym-wrapper around the communication to Webots (http://gym.openai.com/docs/)

The webotsgym is divided in the creation of a webots environment with the options to easily swap reward, observation and action spaces and the communication of the backend with the supervisor, external controller and webots. Everything is built in a modular way to switch between the different approaches (discrete and continuous) and run the training and test runs from the backend without further knowledge about the external controller or webots.

Independent of the action space (discrete, continuous) or the purpose (training, test run) first a new environment has to be initialized. To initialize a new environment a new config has to be created. The default configurations sets all needed parameters for the communication with the external controller and webots. It also sets metrics/metadata for the environment that will be created.

Config options of interest:

* seed : integer		-> option to give a specific and not random seed so that same/different environments can be tested
* sim_mode : SimSpeedMode 	-> increase/decrease the simulation speed in the webots world to train/test faster
* num_obstacles : integer 	-> sets the amount of obstacle in the webots world
* world_size : integer		-> measures of webots world, the created world is a square of world_size x world_size in grids
* world_scaling : integer	-> sets the size of the grids in meter


### Current Configurations - webotsgym/config.py

	# -------------------------- General Settings  ------------------------
        self._direction_type = DirectionType.STEERING
        self.relative_action = None  # if set overwrites action class setting
        self.DIST_VECS = 360  # num of distance vectors
        self.wait_env_creation = 0.5  # in sec
        self.wait_env_reset = 0.5  # in sec
        self.sim_step_every_x = 1  # number of timesteps until next msg is send

        # ------------------------ External Controller ------------------------
        self.IP = "127.0.0.1"
        self.CONTROL_PORT = 6969
        self.BACKEND_PORT = 6970
        self.PACKET_SIZE = 1492
        self.TIME_OFFSET_ALLOWED = 1.0

        # ------------------------ Supervisor ------------------------
        # network settings
        self.IP_S = "127.0.0.1"
        self.PORT_S = 10201
        self.PACKET_SIZE_S = 16

        # setting for world generation via supervisor
        self.seed = None
        self._sim_mode = SimSpeedMode.NORMAL
        self.num_obstacles = 10  # number of obstacles in environment
        self.world_size = 8  # NxN environment measures
        self._world_scaling = 0.5  # meters: 20*0.25 -> 5m x 5m

        # (received) world metadata
        self.gps_target = None  # gps data for target as tuple
        self.sim_time_step = 32  # ms


After the configuration is created, the environment can be created. The backend will setup the environment which holds next to the measures of the worlds in webots also the classes for reward function, action space and observation space of the RL agent. 

### Environment webotsgym/env/webotenv.py
Setup: env = WbtGym(config=config)

Parameters for initialization:

* seed : integer		-> used to setup different Webot environments in *training* in combination with the supervisor mode
* gps_target : tuple		-> define the gps position of the target zone
* train : Boolean		-> if True the trainings mode in the supervisor is activated and the training of a model is possible
* action_class : WbtAct		-> class that holds the action space for the RL agent (more in action section)
* request_start_data : Boolean	-> activate that the backend has to request start of communication
* evaluate_class : WbtReward	-> class that holds the reward function for the RL agent (more in reward section)
* observation_class : WbtObs	-> class that holds the observation space for the RL agent (more in observation section)
* config : WbtConfig		-> the created config for the environment

Because of the big differences between discrete and continuous action space we created next to the main class (WbtGym) also the WbtGymGrid which holds all configurations and settings needed for the discrete action space (webotsgym/env/grid/gridenv). To use the discrete action space you have to do the following:

Setup: env = WbtGymGrid(config=config)

For this class some parameters already have different default classes:

* action_class : WbtActGrid -> default action class for the grid environment
* evaluate_class : WbtRewardGrid -> default reward class for the grid environment
* observation_class : WbtObsGrid -> default observation class for the grid environment

The difference between the input classes of WbtGym and WbtGymGrid you can find in the sections for the specific classes.

### Reward function  


## Use of the WebotsGym and swapping of classes
After the explanation of different modules of our webots environment you can find here some examples for the use of the gym and also the option to overwrite classes directly to alter your own reward functions, action space or observation space: 

### Example 1: Create grid world with own reward function
Here you can find an example how you can alter your own reward function after creating the default WbtGymGrid.
First you create normally the configuration then you can create a new reward class (as WbtRewardGrid) and set your own rewards and also when the episode should finish. 

	config = wg.WbtConfig()
	config.world_size = 8
	config.num_obstacles = 16
	config.sim_mode = wg.config.SimSpeedMode.FAST

	class MyEval(wg.WbtRewardGrid):
	    def __init__(self, env, config, targetband=0.05):
		super(MyEval, self).__init__(env, config)
		self.targetband = targetband

	    def calc_reward(self):
		if self.env.get_target_distance() < self.targetband:
		    reward = 10000
		else:
		    reward = 0

		    # step penalty
		    target_distance = self.env.get_target_distance(normalized=True)
		    step_penalty = -1
		    lambda_ = 5
		    reward += step_penalty * (1 - np.exp(-lambda_ * target_distance))

		    # visited count penalty
		    vc = self.env.gps_visited_count
		    if vc > 3:
			reward += -0.2 * (vc - 2)**2

		    # touching penalty
		    if self.env.state.touching is True:
			reward -= 500

		return reward

	    def check_done(self):
		if self.env.steps_in_run == 200:
		    return True
		if self.env.total_reward < -1000:
		    return True
		if self.env.get_target_distance() < self.targetband:
		    return True
		return False
		
	env = wg.WbtGymGrid(config=config,
                    evaluate_class=MyEval)



### Example 2: Create continuous world with own reward function
Same procedure as with the first example. This time only in the continuous action space.

	config = wg.WbtConfig()
	config.world_size = 3
	config.num_obstacles = 0
	config.sim_mode = wg.config.SimSpeedMode.RUN
	config.sim_step_every_x = 5
	
	class MyEval(wg.WbtReward):
		def __init__(self, env, config: wg.WbtConfig = wg.WbtConfig()):
			super(MyEval, self).__init__(env, config)

		def calc_reward(self):
			if self.env.get_target_distance() < 0.05:
            			reward = 10000
        		else:
            			reward = -1
        		return reward

		def check_done(self):
			if self.env.get_target_distance() < 0.05:
            			return True
        		if self.env.steps_in_run % 2500 == 0:
            			return True
        		return False
	
	env = wg.WbtGym(config=config, evaluate_class=MyEval)


### Action and observation space
In the same way as we altered the reward class we can also setup a new action or observation space. For this please take a look into the following files:
* Continuous action class: webotsgym/env/action/continuous.py
* Discrete action class: webotsgym/env/action/discrete.py
* Grid action class: webotsgym/env/grid/action.py
* Continuous observation class: webotsgym/env/observation/observation.py
* Grid observation class: webotsgym/env/grid/observation.py

### environment - webotsgym/environment.py
* `from webotsgym.environment import webotsgym`
* load environment by `env = webotsgym()`
* Main arguments:
    * `seed`, used to setup different Webot environments in *training* in combination with the supervisor mode
    * `action_class`, used to setup the `action_space` and the mapping of the actions to webots actions via `map()`. For example: `action_class=DiscreteAction(directions=3, speeds=3, mode="flatten")` will setup a discrete Action space of size 9. Possile actions to be calculated by an agent (e.g. openai model) are 0:8. *map()* is used to translate the action index to a webot action. Example 0: decrease speed, turn left. For more information of the mapping see *DiscreteAction* in **action.py**. Another possiblity is `action_class=ContinuousAction`, this will set the *action_space=[-1, 1]^2* with a direct mapping.
    * `evaluate_class`, uses the environment information to `calc_reward()` for the *last action* resulting in the *current state*. Evaluate class is used to check whether iteration is finished via `check_done()`. For different reward options see **evaluate.py**.
    * `observation_class`, used the environment to setup an observation to be fed to the agent in the `step()` function. Specify custom observations in **observation.py**.
* make a action step by `state, reward, done, {} = env.step(action)`.
* To get the information of the communication, call appropriate action on `env.com`


### Interface for automated testing - webotsgym/automate.py
```

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
	int return_code;         // return_code [int]
	int sim_time_step;       // simulation time_step in ms [int]
	float target[2];         // target gps [float]
} __attribute__((packed)) sv_to_bcknd_msg_t;

// supervisor <-- backend
typedef struct {
	enum function_code function_code; // function code [enum function_code]
	int seed;                         // seed [int]
	int fast_simulation;              // fast_simulation [int]
	int num_obstacles;                // num_obstacles [int]
	int world_size;                   // world_size in blocks [int]
	float world_scaling;              // world grid size in meters [float]
} __attribute__((packed)) bcknd_to_sv_msg_t;

```

### Interface to external controller - webotsgym/communicate.py
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
