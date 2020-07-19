from enum import IntEnum


class SimSpeedMode(IntEnum):
    """GET ENUM for simulation speed.

    Parameter:
    ----------
    IntEnum : str
    """

    NORMAL = 0
    RUN = 1
    FAST = 2


class DirectionType(IntEnum):
    """GET ENUM for direction type.

    Parameter:
    ----------
    IntEnum : str
    """

    STEERING = 0  # PID-Controller is off
    HEADING = 1  # PID-Controller is on


class DiscreteMove(IntEnum):
    """GET ENUM for move direction in discrete action space.

    Parameter:
    ----------
    IntEnum : str
    """

    NONE = 0
    UP = 1
    LEFT = 2
    DOWN = 3
    RIGHT = 4


class WbtConfig():
    """Create settings for config between backend and controller/webots."""

    def __init__(self):
        """Initialize config class for backend, controller & supervisor."""
        # -------------------------- General Settings  ------------------------
        self._direction_type = DirectionType.STEERING
        self.relative_action = None  # if set overwrites action class setting
        self.DIST_VECS = 360  # num of distance vectors
        self.wait_env_creation = 0.5  # in sec
        self.wait_env_reset = 0.5  # in sec
        self.sim_step_every_x = 1  # number of timesteps until next msg is send
        self.timeout_after = 5  # in sec

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

    def print_config(self):
        """Print config class with max length."""
        for (k, v) in sorted(self.__dict__.items()):
            print(str(k).ljust(20) + str(v))

    @property
    def sim_mode(self):
        """Get simulation mode."""
        return self._sim_mode

    @sim_mode.setter
    def sim_mode(self, value):
        """Set simulation mode.

        Parameter:
        ----------
        value : str
            ["normal", "run", "fast"]
        """
        if isinstance(value, SimSpeedMode):
            self._sim_mode = value
        elif value == "normal":
            self._sim_mode = SimSpeedMode.NORMAL
        elif value == "run":
            self._sim_mode = SimSpeedMode.RUN
        elif value == "fast":
            self._sim_mode = SimSpeedMode.FAST

    @property
    def direction_type(self):
        """Get direction type."""
        return self._direction_type

    @direction_type.setter
    def direction_type(self, value):
        """Set direction type.

        Parameter:
        ----------
        value : str
            ["heading", "steering"]
        """
        if isinstance(value, DirectionType):
            self._direction_type = value
        elif value == "steering":
            self._direction_type = DirectionType.STEERING
        elif value == "heading":
            self._direction_type = DirectionType.HEADING

    @property
    def world_scaling(self):
        """Get world scaling."""
        return self._world_scaling

    @world_scaling.setter
    def world_scaling(self, value):
        """Set world scaling with more than 0.25 or equal.

        Parameter:
        ----------
        value : float
            parameter to scale the environment.
        """
        if value < 0.25:
            raise ValueError("world_scaling must be larger or equal 0.25")
        self._world_scaling = value
