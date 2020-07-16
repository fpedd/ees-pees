# User Guide
- [User Guide](#user-guide)
  * [Setup](#setup)
    + [OS](#os)
    + [Webots](#webots)
    + [Python Packages](#python-packages)
    + [Stable-Baselines](#stable-baselines)
  * [Usage Example](#usage-example)
    + [Manual Control](#model-training)
    + [Automated Training and Application](#model-appilication)




## Setup

### OS
Ubuntu 18.04
### Webots
A tutorial on how to install Webots can be found [here](https://cyberbotics.com/doc/guide/installation-procedure).

In order for our software to know where your Webots installation is located at, you will need to set an environment variable. The name of the environment variable you need to set is: `WEBOTS_HOME`. It should point to your Webots installation. If you installed Webots the "normal" way (see below), setting the variable will look like this: `export WEBOTS_HOME=/usr/local/webots`.

In order to not always have to type and execute that in your terminal, you can add this command to the bottom of your `.bashrc` file. You can find this file in your home directory. The contents of the `.bashrc` get executed every time you open a new terminal.

The bottom of your `.bashrc` should look something like this.
```
...

# Webots Installation
export WEBOTS_HOME=/usr/local/webots
```
Please open Webots once and do the setup before continuing. 

### Python Packages
To use our software, you'll need to install several python packages. Please use `requirements.txt` to install the python packeages:
```
pip freeze > requirements.txt
pip install -r requirements.txt
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
### Manual Control

To start the communication stack, you can run `./run.sh` in the root directory of the repository. This should compile the Internal and the External Controller. After that is done, it will start the External Controller, then the Webots Environment with the Internal Controller, and after that is the Python Backend.

You will see three corresponding terminals open with the three processes mentioned above run from each terminal. Inside the top terminal, the Python Backend should be running.

You are able to drive the robot by your own in the discrete or continuous action space. You can use the space bar to switch between discrete and continuous action spaces. With the keyboard, you can increase or decrease the speed change the heading in the continuous action space by the default. In the discrete action space, every keypress will trigger an action in the respective direction.

To stop all processes, just run `./kill.sh`. This will kill all three processes.

Before you will be able to run the scripts you may need to run:  
`chmod +x kill.sh`  
`chmod +x run.sh`

### Automated Training and Application

In the `UseMe` directory, there are several notebooks for you to train and apply the model on the Webots environment.

To train a model you can use the notebooks below:
* `UseMe/model_training_fake_environment.ipynb`, train a grid model in fake environment. Since the fake environment is a mapping of Webots grid environment, the model can be used in Webots grid environment.
* `UseMe/model_training_grid_world.ipynb`, train a grid model in Webots grid environment. The model can be used in Webots grid environment.
* `UseMe/model_training_continuous_world.ipynb`, train a grid model in Webots continuous environment. The model can be used in Webots continuous environment.

To apply a trained model to Webots environment, you can use these two notebooks:
* `UseMe/model_application_grid_world.ipynb`
* `UseMe/model_application_continuous_world.ipynb`

We have already trained a excellent model `UseMe/model/grid/PPO_lam3+vs_500k.zip` for Webots grid environment. Highly recommand to use it in `UseMe/model_application_grid_world.ipynb`.
