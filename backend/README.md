# EES-PEES Robot Project Backend

## Overview backend
* fakegym -> code and notebooks to train and run a RL agent on our self created fake environment
* research -> old notebooks with our first attempts to create RL agents
* test -> unit and integration tests for the webots environment and fake environments
* webotsgym -> heart of the backend with code to train and run a RL agent on the webots environment
* james.py -> wrapper class to control the robot on your own in the webots environment

For insights into the fake environment, research or the test please have a look into the regarding folder.
In the following you can find a closer view on the functionalities of the webotsgym and what is possible from a more technical perspective. 


## Overview Readme
* Webotsgym -> how to setup an environment and add different modular input
* Reward class -> class to calculate the reward of each action for RL and when episode is finished
* Action class -> three different default action classes for discrete and continuous environments
* Observation class -> two different observation classes with data from webots environment
* Communication -> classes which manage the communication with external controller and supervisor for training and test runs
* Use of Webotsgym -> how to run training and test runs with customized reward, action and observation classes

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
* timeout_after : float		-> to avoid problems during the training we reset the environment every 5 seconds after a timeout (no package received)*

*With timeout_after = 0 you can deactivate this option because also a break would initialize the reset directly after 5 seconds.


### Current Configurations - webotsgym/config.py

	# -------------------------- General Settings  ------------------------
        self._direction_type = DirectionType.STEERING
        self.relative_action = None  # if set overwrites action class setting
        self.DIST_VECS = 360  # num of distance vectors
        self.wait_env_creation = 0.5  # in sec
        self.wait_env_reset = 0.5  # in sec
        self.sim_step_every_x = 1  # number of timesteps until next msg is send
	self._timeout_after = 0  # in sec

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

### Reward class
For each of the two gyms (WbtGym and WbtGymGrid) the default reward classes are added as a default in the initialization. 
As we have two gyms we have also two subclasses classes: webotsgym/env/reward/reward.py

The reward class has two components: calc_reward and check_done

#### WbtRewardContinuousV1:
- calc_reward
	
		The default reward function is divided into a reward if the robot
        reaches the target zone (reward up to 1000) and a step reward.
	
        If the robot reaches the target zone it gets a reward of 500 and
        up to 500 more depending on the speed the robot has reaching the zone.
        The slower the robot is the better, so the robot learns to actually
        stop in the target zone and not only reach it with whatever speed
        possible.

        The robot gets for each step a reward or penalty depending on the
        distance to the target zone, if the robot moved during the last step
        closer to the target zone or more far away from it. If it moved closer
        it gets a positive reward up to 500.
        If it moved away from the target zone a reward up to -500.

        If an action was denied by the webots or backend because of safety
        compliance the robot gets another penalty of -1.

        The negative reward is even more decrease if webots signal us that with
        the performed action an object (wall or obstacle) was touched/hit.
        For this the robot gets a reward of another -20.

- check_done

		For the continuous space the function sets the episode on done if
        - 500 or more steps are performed.
        - total reward went to lower than -1000
        - the target zone was reached
        - total reward went to higher than 2000

        With this measures we ensure that the robot resets the environment
        often enough and learns faster if it got stuck,hit a lot of obstacles
        or came close enough to the goal.


#### WbtRewardGrid:
- calc_reward
	
		The default reward function is divided into a reward if the robot
        reaches the target zone (reward of 10000) and a negative step reward.

        The negative step reward consists out of a negative reward depending
        on the distance to the target, the visited count and if an object was
        touched/hit or not.
        If the robot moves closer to the target it gets a smaller negative
        award than staying as far as before. For moving away the penalty
        increases all normalized between 0 and -1 as the maxium.

        The visited count gives a negative reward after the robot visited
        more than 2 times the same gps position with an exponential negative
        reward.

        The negative reward is even more decrease if webots signal us that with
        the performed action an object (wall or obstacle) was touched/hit.
        For this the robot gets a reward of another -500.

- check_done

		For the grid world the function sets the episode on done if
        - more than 200 steps are performed.
        - total reward went to lower than -1000
        - the target zone was reached

        With this measures we ensure that the robot resets the environment
        often enough and learns faster if it got stuck or
        hit a lot of obstacles.
	

These two reward classes can be easily overwritten to create your own reward class for training. How you can overwrite the default reward functions you find in the section about how to use WebotsGym and the swapping of classes.


### Action class
Also for the action class we have different classes. Here we actually have 3 different classes. One class is for the grid world (webotsgym/env/grid/action.py), the other two are for the continuous action space (webotsgym/env/action/continuous.py & webotsgym/env/action/discrete.py) and differ by how "continuous" the actions are.

#### WbtActContinuous webotsgym/env/action/continuous.py
This action class actually allows completely continuous actions for direction and speed from [-1 to 1]. You can set a bound for the class which can limit the maximum of the space. For absolut actions it is fixed to (1,1).

#### WbtActDiscrete webotsgym/env/action/discrete.py
This action class gives fix values for the direction and speed so that the action space is actually not continuous anymore but still quite big by size.
The possible actions are the following:

	Generate matrix of possible actions. Rows are possible speeds, columns possible directions. The following symetric grid is generated by settings:
        direcstions = 5
        range_direction = 0.3
        speeds = 3
        range_speed = 0.1
        NOTE: range_ should be a float in (0, 1] as it specifies the endpoints
              of the action grid.

                            DIRECTIONS
            +------+ +------+-------+---+------+-----+
            |      | | -0.3 | -0.15 | 0 | 0.15 | 0.3 |
        S   +------+ +------+-------+---+------+-----+
        P   +------+ +------+-------+---+------+-----+
        E   | -0.1 | | 0    | 1     | 2 | 3    | 4   |
        E   +------+ +------+-------+---+------+-----+
        D   | 0    | | 5    | ...   |   |      |     |
        S   +------+ +------+-------+---+------+-----+
            | 0.1  | |      |       |   |      |     |
            +------+ +------+-------+---+------+-----+
            Example: RL-agent action = 4 is mapped to (0.3, -0.1).


#### WbtActGrid webotsgym/env/grid/action.py
This class is the action class for the grid world and only allows 4 different actions (up, down, left, right). For this reason it maps also the actions from models that are trained on the fake environment to the webots environment so that these models actually can be used.

Mapping from fake to webots environment:

    0: Right -> Up    (1)
    1: Down  -> Left  (2)
    2: Left  -> Down  (3)
    3: Up    -> Right (4)



All three classes can be used in their underlying environments but also overwritten for different purposes.

### Observation class
For the observation we have again two classes, one for the grid action space (webotsgym/env/grid/observation.py) and one for the continuous action space (webotsgym/env/observation/observation.py). They differ mainly by the size of the observation space and also what kind of information we retrieve from the webots environment to calculate the next action: 

#### WbtObs webotsgym/env/observation/observation.py
WbtObs creates the default observation space in the continous env. The lidar data is mapped from 360 to only 12 data points to reduce complexity so that the observation space has a shape of 22.

    sim_time:   1  -> current simulation time to adjust accordingly
    gps_actual: 2  -> gps from current position
    gps_target: 2  -> gps of target zone
    speed:      1  -> current speed of the robot
    heading:    1  -> info about the heading of the robot
    steering:   1  -> info about the steering of the robot
    touching:   1  -> flag if the robot touched a wall or obstacle
    act_denied: 1  -> flag to give feedback if action was denied
    lidar:     12  -> mapped from originally 360 to 12 data points to
                          reduce complexity for RL in continuous action space
    -------------
    total:     22

#### WbtObsGrid webotsgym/env/grid/observation.py
The grid environment has different observation space as the continuous.The lidar data is mapped to the 4 action direction and the observation space has a shape of 10.

    gps_actual:         2  -> gps from current position
    gps_target:         2  -> gps of target zone
    lidar:              4  -> lidar mapped from 360 to the 4 directions
    act_denied:         1  -> flag to give feedback if action was denied
    visited_count:      1  -> count for how often position was visited already
    ---------------------
    total:             10

Also these observation classes can be overwritten and used in a customized way when initializing the WebotGym and WebotGridGym.

### Communication with Webots, External Controller and Supervisor
There are different classes that organize and manage the communication of the backend with webots, external controller and the supervisor. There is the communication class, the packetIn/Out classes, WbtCtrl class and ExtCtrl class.

#### WbtCtrl webotsgym/com/automate/supervisor.py
The WbtCtrl class organizes the communication with Webotscontroller/Supervisor in an autonomous way. It can initialize webots, environment and external controller but also compile all controllers, open webots, establish the tcp connection and start, reset and close environments. With this whole stack of functionalities it is managing the communication and setup for the trainingspart. 


#### ExtCtrl webotsgym/com/automate/extcontroller.py
The ExtCtrl is the class that starts, resets, compile and closes the external controller and has so full access to all functionalities to trigger all needed functionalities from the backend to the external controller.


#### Communication webotsgym/com/communicate.py
The communication class is the main class to setup the socket connection, receive and send packets from the backend to the external controller. Here also the moves from the RL agent are transmitted. 


#### PacketIn/PacketOut webotsgym/com/package.py
The classes PacketIn and PacketOut manage the actual packets that are received and sent from the backend. PacketIn handles the packet that gets received from the external controller and PacketOut handles the package that the backend sends to the external controller. 


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
