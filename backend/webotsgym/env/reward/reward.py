from webotsgym.config import WbtConfig
from webotsgym.env.reward.steppenalty import step_pen_exp
import webotsgym.utils as utils


class WbtReward():
    """Create general reward class for RL agent learning.

    Parameter:
    ---------
    env : WbtEnv

    config : WbtConfig

    targetband : float
        radius for the target zone

    """

    def __init__(self, env, config: WbtConfig = WbtConfig()):
        """Initialize WbtReward class."""
        self.env = env
        self.config = config
        self.targetband = 0.05

    def calc_reward(self):
        """Create reward function which gives general reward back.

        Description:
        ------------
        The reward function is the heart of the RL approach.
        After an action is performed the function gives back
        a reward attached to the action based on the observation space.

        Here you can find a simplified function because they are overwritten
        for the different action space (discrete and continuous) in
        the subclasses.
        If the robot reaches the target zone it gets a fixed reward of 10000.
        Otherwise it gets a step penalty of -1

        Return:
        -------
        integer
            reward associated to action depending of the observation state.

        """
        if self.env.get_target_distance() < self.targetband:
            reward = 10000
        else:
            reward = -1
        return reward

    def check_done(self):
        """Create function which checks if we reached the end of one episode.

        Description:
        ------------
        The check_done function is different from environment and
        action space and gets overwritten for each trainingsrun
        depending on what to test and run.

        The simplified function here, gives back that the episode
        is done (finished) if we reach the target zone or after 2500 steps.

        Return:
        -------
        Boolean
            True  -> episode is done (finished) after the last action
            False -> episode is not done and continues with next step

        """
        if self.env.get_target_distance() < self.targetband:
            return True
        if self.env.steps_in_run % 2500 == 0:
            return True
        return False


class WbtRewardGrid(WbtReward):
    """Create reward class for RL agent learning in grid action space.

    Parameter:
    ---------
    env : WbtEnv

    config : WbtConfig

    targetband : float
        radius for the target zone

    """

    def __init__(self, env, config, targetband=0.05):
        """Initialize WbtRewardGrid class which is a subclass to WbtReward."""
        super(WbtRewardGrid, self).__init__(env, config)
        self.targetband = targetband

    def calc_reward(self):
        """Create default reward function for the grid (discrete) action space.

        Description:
        ------------
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

        Return:
        -------
        integer
            reward associated to action depending of the observation state.

        """
        if self.env.get_target_distance() < self.targetband:
            reward = 10000
        else:
            reward = 0

            # step penalty
            target_distance = self.env.get_target_distance(normalized=True)
            reward += step_pen_exp(target_distance, step_penalty=-1,
                                   lambda_=5)

            # visited count penalty
            vc = self.env.gps_visited_count
            if vc > 3:
                reward += -0.2 * (vc - 2)**2

            # touching penalty
            if self.env.state.touching is True:
                reward -= 500

        return reward

    def check_done(self):
        """Create function which checks if we reached the end of one episode.

        Description:
        ------------
        For the grid world the function sets the episode on done if
        - more than 200 steps are performed.
        - total reward went to lower than -1000
        - the target zone was reached

        With this measures we ensure that the robot resets the environment
        often enough and learns faster if it got stuck or
        hit a lot of obstacles.

        Return:
        -------
        Boolean
            True  -> episode is done (finished) after the last action
            False -> episode is not done and continues with next step

        """
        if self.env.steps_in_run == 200:
            return True
        if self.env.total_reward < -1000:
            return True
        if self.env.get_target_distance() < self.targetband:
            return True
        return False


class WbtRewardContinuousV1(WbtReward):
    """Create reward class for RL agent learning in continuous action space.

    Parameter:
    ---------
    env : WbtEnv

    config : WbtConfig

    targetband : float
        radius for the target zone

    """

    def __init__(self, env, config):
        """Initialize WbtRewardContinuousV1 class for subclass WbtReward."""
        super(WbtRewardContinuousV1, self).__init__(env, config)

    def calc_reward(self):
        """Create default reward function for the continuous action space.

        Description:
        ------------
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

        Return:
        -------
        integer
            reward associated to action depending of the observation state.

        """
        target_distance = self.env.get_target_distance(False)
        if target_distance < 0.1:
            return 500 + 500 * (1 - abs(self.env.state.speed))
        else:
            reward = 0
            if self.env.steps_in_run > 1:
                reward += -1

                # get distance moved towards target in last step
                move_to_goal = self.env.distances[-2] - self.env.distances[-1]

                # calculate total distance moved in last step
                gps_current = self.env.history[-1].gps_actual
                gps_last = self.env.history[-2].gps_actual
                move_total = utils.euklidian_distance(gps_current, gps_last)

                # how much of our move got us closer to the goal
                move_diff_ratio = move_to_goal / move_total

                # compared to the start, how close are we to the goal
                diff_initial = self.env.distances[0]
                diff_ratio = abs(move_to_goal / diff_initial)

                # get closer, get reward. Move away, negative penalty.
                if move_total > 0:
                    diff_rew = 500 * diff_ratio * move_diff_ratio
                else:
                    diff_rew = 0

                reward += diff_rew

            if self.env.state.action_denied:
                reward += -1

            if self.env.state.touching:
                reward += -20
        return reward

    def check_done(self):
        """Create function which checks if we reached the end of one episode.

        Description:
        ------------
        For the continuous space the function sets the episode on done if
        - 500 or more steps are performed.
        - total reward went to lower than -1000
        - the target zone was reached
        - total reward went to higher than 2000

        With this measures we ensure that the robot resets the environment
        often enough and learns faster if it got stuck,hit a lot of obstacles
        or came close enough to the goal.

        Return:
        -------
        Boolean
            True  -> episode is done (finished) after the last action
            False -> episode is not done and continues with next step

        """
        if self.env.total_reward < -1000:
            return True

        if self.env.steps_in_run > 500:
            return True

        if self.env.get_target_distance(False) < 0.1:
            return True

        if self.env.total_reward > 2000:
            return True

        return False
