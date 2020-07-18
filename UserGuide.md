# User Guide
- [Setup](#setup)
  * [OS](#os)
  * [Webots](#webots)
  * [Python Packages](#python-packages)
  * [Stable-Baselines](#stable-baselines)
- [Usage Example](#usage-example)
  * [Manual Control](#manual-control)
  * [Automated Training and Application](#automated-training-and-application)

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
To use our software, you'll need to install several python packages. Please use `requirements.txt` to install the python packages:
```
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

To start the application for manual control, you can run  TODO `scripts/run.sh` in  directory of the repository. This should compile the Internal and the External Controller. After that is done, it will start the External Controller, then the Webots Environment with the Internal Controller, and after that the Python Backend.

You will see three corresponding terminals open with the three processes mentioned above run from each terminal. Inside the top terminal, the Python Backend should be running.

You are able to drive the robot on your own using either discrete (move from one tile to another) or continuous actions. Press space to switch between both control modes. With the arrow keys, you can increase or decrease the speed and steer in the continuous action space. In the discrete action space, every keypress will trigger an action in the respective direction where the directions are seen absolute and not from the robots perspective.

To stop all processes, just run TODO `scripts/kill.sh`. This will kill all three processes.

Before you will be able to run the scripts you may need to run:  
`chmod +x kill.sh`  
`chmod +x run.sh`

### Automated Training and Application

In the `UseMe` directory, there are several notebooks for you to train and apply the model on the Webots environment.

To train a model you can use the notebooks below:
* [`UseMe/model_training_fake_environment.ipynb`](UseMe/model_training_fake_environment.ipynb) to train a model in the fake environment (grid actions). The training is then done in the "fakegym". This environment simulates the Webots grid environment. Therefore the model can be used in the [Webots grid environment](UseMe/model_application_grid_world.ipynb) afterwards.
* [`UseMe/model_training_grid_world.ipynb`](UseMe/model_training_grid_world.ipynb) to train a model in the Webots grid environment. This should lead to the same result as training in the fake environment, but take significantly more time. The model can be used in the [Webots grid environment](UseMe/model_application_grid_world.ipynb).
* [`UseMe/model_training_continuous_world.ipynb`](UseMe/model_training_continuous_world.ipynb) to train a model in the Webots continuous environment. However the default training time of 100000 timesteps is not long enough to see results. First improvements can be seen after 1-2 million steps (taking 6-8 hours at a simulations speed of about 40x). The model can be used in Webots continuous environment.

To apply a trained model to Webots environment, you can use these two notebooks for corresponding environment:
* [`UseMe/model_application_grid_world.ipynb`](UseMe/model_application_grid_world.ipynb)
* [`UseMe/model_application_continuous_world.ipynb`](UseMe/model_application_continuous_world.ipynb)

We have already trained an excellent model `UseMe/model/grid/PPO_lam3+vs_500k.zip` for Webots grid environment. We recommend to use it in [`UseMe/model_application_grid_world.ipynb`](UseMe/model_application_grid_world.ipynb). It can solve most environments reliably. Due to the prolonged training times in the continuous environment, which still don't lead to a model that can be considered as "solving" any environment, we cannot provide a pre trained model for this.

You might encounter "port already in use" errors, if the connection is not closed correctly. In that case you will receive a message in the python notebook: 
```
Port blocked due to incorrect closing of connection. Use 'webotsgym.com.kill_spv_connection(password)' or command 'sudo lsof -t -i tcp:10201 | xargs kill -9'. Both approaches will kill the current python process. Therefore the jupyter notebook must be rerun from the beginning.
Enter password to kill process:
```

Please enter your password to easily kill the process or manually excecute the command in a terminal. Afterwards you need to rerun the notebook.
