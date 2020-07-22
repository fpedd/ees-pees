# Group name
**Group members**: *Your names*
 - Mats Kipper
 - Jonas Dommes
 - Shanshan Yi
 - Fabian Peddinghaus
 - Rui Li
 - Wladimir Assmann
 - Per Joachims


## Project overview
A **short** summary of your project topic.

### Goals
What were your main goals?

### Requirements
List the **necessary** and **optional** requirements that were set for your project.

- Requirement 1
- Requirement 2
- Requirement 3

### Approach
How have you tried to meet the above requirements? What were your ideas?

- Approach 1
- Approach 2
- Approach 3

## System architecture
Some **general** information about your ideas to the overall system architecture.

### Software design


![diagram](./images/software_design.svg)

### Robot design
What does your robot look like, and what functionality does it contain.
But most of all: **Why** did you choose this design?

![robot](./images/robot.png)

### Environment design
What does the environment look like in which your robot operates?
The same: **Why** did you choose this environment?

![evironment](./images/environment.png)

### Algorithms
Write an introduction to the **most essential** algorithms or technologies in general that you have chosen for your project.

Maybe with **short** code examples.

```python
def our_algorithm(x, y):
    # Do fancy stuff here
    return {'x': x, 'y': y}
```

## Summary
Overview of the achieved **and** not attained goals. Why were some goals not reached? Too difficult or wrong time management?
ATTAINED:
 - Setup Webots world and communication stack to the backend
 - Build a wrapper to use Webots as a gym environment, enabling us to train the algorithms from stable baselines
 - Incorporate safety layer to have a safe reinforcement learning environment where the robot does not crash even while training
 - Successfully train a PPO1 on our WbtGymGrid

NOT ATTAINED:
 - Successfully train a PPO1

### Lessions learned
What did you learn from the project? What decisions would you have made differently from your current perspective?

### Future work
What problems would you tackle if you would continue to work on the project? Are there things you might actually take up and work on in the future? This part is **optional**.
