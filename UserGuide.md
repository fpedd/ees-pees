# User Guide
- [User Guide](#user-guide)
  * [Setup](#setup)
    + [OS](#os)
    + [Webots](#webots)
    + [Python Packages](#python-packages)
    + [Stable-Baselines](#stable-baselines)
  * [Usage Example](#usage-example)
    + [Model Training](#model-training)
      - [Fake environment](#fake-environment)
      - [Webots grid environment](#webots-grid-environment)
      - [Webots continuous environment](#webots-continuous-environment)
    + [Model Appilication](#model-appilication)
      - [Webots grid environment](#webots-grid-environment-1)
      - [Webots continuous environment](#webots-continuous-environment-1)



## Setup

### OS
Ubuntu 18.04
### Webots
A tutorial on how to install webots can be found [here](https://cyberbotics.com/doc/guide/installation-procedure).

In order for our software (compiler, python, etc.) to know where your webots installation is located at, you will need to set an environment variable. The name of the environment variable you need to set is: `WEBOTS_HOME`. It should point to your webots installation. If you installed webots the "normal" way (see below), setting the variable will look like this: `export WEBOTS_HOME=/usr/local/webots`.

In order to not always have to type and execute that in your terminal, you can add this command to the bottom of your `.bashrc` file. You can find this file in your home directory. The contents of the `.bashrc` get executed every time you open a new terminal.

The bottom of your `.bashrc` should look something like this.
```
...

# Webots Installation
export WEBOTS_HOME=/usr/local/webots
```
Please open webots once and do the setup before continuing. 

### Python Packages
To use our software, you'll need to install the following python packages, please use `pip` for that. 
```
pip install pynput==1.6.8
pip install psutil==5.6.7
pip install matplotlib==3.1.3
pip install numpy==1.18.1
pip install pathfinding
pip install gym
```
### Stable-Baselines
Our reinforcement learning agent is based on Stable-Baselines. It requires python3 (>=3.5) with the development headers. You’ll also need system packages CMake, OpenMPI and zlib. 
```
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
```
Stable-Baselines supports Tensorflow versions from 1.8.0 to 1.15.0, and does not work on Tensorflow versions 2.0.0 and above. 

To install with support for all algorithms,  execute:
```
pip install stable-baselines[mpi]
```
A detailed document of Stable-Baselines can be found [here](https://stable-baselines.readthedocs.io/en/master/index.html).


## Usage Example

See the `UseMe` directory.
* Run ` ` to train a model in fake environment
* Run `UseMe/model_training_grid_world.ipynb` to train a model in Webots grid environment
* Run `UseMe/model_training_continuous_world.ipynb` to train a model in Webots continuous environment
* Run `UseMe/model_application_grid_world.ipynb` to applicate a model in Webots grid environment
* Run `UseMe/model_application_continuous_world.ipynb` to applicate a model in Webots continuous environment

We have already trained several models in `UseMe/model` directory for application. The models in `UseMe/model/grid` directory can be applied in Webots grid environment, and `UseMe/model/grid` directory includes the models for Webots continuous environment.

### Model Training

#### Fake environment
Before training in fake environment you can setup these parameters:
* `...`

You can create your own reward function, these following variables and methods are for your use：
* `...`

The model trained in fake environment can be transferred to apply in Webots grid environment.
#### Webots grid environment
Run `UseMe/model_training_grid_world.ipynb` to train a model in Webots grid environment. Before training in Webots grid environment you can setup these parameters:
* `config.world_size` , setup the size of Webots environments for training. For example: `config.world_size = 8` will setup a square map of size 8x8 in Webots.
* `config.num_obstacles`, setup the number of obstacles. Each obstacle is a block of size 1x1.
* `config.sim_mode`, used to setup the speed of the simulation of Webots. 
`config.sim_mode = wg.config.SimSpeedMode.NORMAL`, run the simulation in the Real-Time mode.
`config.sim_mode = wg.config.SimSpeedMode.RUN`, run the simulation as fast as possible using all the available CPU power. 
`config.sim_mode = wg.config.SimSpeedMode.FAST`, run the simulation as fast as possible without the graphics rendering, hence the 3d window is black.
* `time_steps`, setup the total number of samples to train on. It is recommended that you set this parameter to greater than 100000, then you will get a relatively stable model.
* `model_name`, name the model for saving. The model will be saved in `UseMe/model/grid` directory after training complete.

You can create your own reward function, these following variables and methods are for your use：
* `self.env.get_target_distance()`, some description balabalabala
* `self.env.gps_visited_count`
* `self.env.state.touching`
* `self.targetband`
* `self.state.action_denied`
* `...`




#### Webots continuous environment
Run `UseMe/model_training_continuous_world.ipynb` to train a model in Webots continuous environment. The setup is similar with the training in Webots grid environment. You can follow the guide in Webots grid environment except:
* `time_steps`, setup the total number of samples to train on. It is recommended that you set this parameter to greater than ???, then you will get a relatively stable model.
* `model_name`, name the model for saving. The model will be saved in `UseMe/model/continuous` directory after training complete.

And for rewards there are also some difference:
* `...`
### Model Appilication
After training your own model, you can apply it to Webots environment. Besides, you can use our trained model in `UseMe/mode` directory. The model can only be used in the corresponding environment.
#### Webots grid environment
Run `UseMe/model_application_grid_world.ipynb` to applicate a model in Webots grid environment. Before application in Webots grid environment you need to setup these parameters:
* `config.world_size` , setup the size of Webots environments for training. For example: `config.world_size = 8` will setup a square map of size 8x8 in Webots.
* `config.num_obstacles`, setup the number of obstacles. Each obstacle is a block of size 1x1.
* `config.sim_mode`, used to setup the speed of the simulation of Webots. 
`config.sim_mode = wg.config.SimSpeedMode.NORMAL`, run the simulation in the Real-Time mode.
`config.sim_mode = wg.config.SimSpeedMode.RUN`, run the simulation as fast as possible using all the available CPU power. 
`config.sim_mode = wg.config.SimSpeedMode.FAST`, run the simulation as fast as possible without the graphics rendering, hence the 3d window is black.
* `model_name`, name of the model you use. The model will be loaded from `UseMe/model/grid` directory.
* ` num_of_steps`, setup the step limit for one environment. For example, `num_of_steps = 100` means the agent must reach the target area within 100 steps. Otherwise, this environment will be judged as unsolved.
* ` num_of_envs`, setup the number of environments for model application. 

result figure discription balabalabala
[figure]
[figure]

You can also compare several models with changing the model loading part like this:
```python
model1_name = "Model1Name"
model2_name = "Model2Name"
model1 = PPO1.load("model/grid/{}".format(model1_name))
model2 = PPO1.load("model/grid/{}".format(model2_name))
models = [model1, model2]
names = ["Model1Name","Model2Name"]
```

This is a sample of figure when comparing serveral models.
[figure]
#### Webots continuous environment
Run `UseMe/model_application_continuous_world.ipynb` to applicate a model in Webots continuous environment. The setup is similar with the application in Webots grid environment. You can follow the guide in Webots grid environment except:
* `config.sim_step_every_x`, balabalabala
* `config.relative_action`
* `config.direction_type`
* `num_of_steps`
