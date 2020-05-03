
## Meeting on 04.05.2020
#### Agenda
* All
  * What is a good communication protocol for between the layers? That depends on
    the connection, the sensors, and where the information is encoded / decoded.
    (example Video: maybe dont transmit video data. Use local algorithms to extract
    depth / distance information locally?)
  * Where should the safety happen? In the NN? Or in the controller? Or both?


* Backend Team
  * has to work on theory behind RL and figure out a good architecture.
  * What NN should we use (maybe have a couple at the ready that we can test?).
  * Then find a concept on how to train that network. What is a good reward function?
  * Figure out a high level controller that controls the mission.
  * Figure out what sensor data we need. What form it should be in, in order to
    to be usable for the NN.
  * Also look at SLAM and NN.
  * What is the output of the NN? A direction? Actual motor commands?


* Controller Team
  * Build a robot
    * Select sensors
    * Select actuators
    * Select shape and form
    * Build the webots controller for that robot
  * get the environments setup that we can train the robots in. What should it
    look like?
  * get the communication protocol working. Provide the backend team with a
    reasonable interface that they can use in python. Therefore write a python
    wrapper that can help the backend team (they will have enough to do...)
  * Find a way to automate training. Using scripts / supervisor controller /
    webots fast mode etc. The backend team needs a way to get their reinforcement
    stuff going. Look into supervisor controller to move the robot to desired points
    -> could help make training simpler.

#### Interesting
* Maybe, to make things easier, simpler and more "greifbar", we should narrow down
  our project to a real world application. That would help to "very naturally"
  clear up a lot of questions now and in the future. For example: we are building
  a kitchen cleaning robot that works in kitchens and has to get back to its
  charging station (it does not know its environment at the start of our challenge).
  Or: We are building a drug delivery robot that delivers drugs through a city?
* Webots can be started from a script, you can options such as fast mode and
  logging to an external file, this could be interesting for automated training
* Should we use spaces or tabs in C? Webots examples use 1 space (WTF)?
* Lets completely stick to c code for all controller stuff (webots and external).
  We all know c better than c++. All examples and apis in webots are basically
  written in c.  
* Depending on the environment our robot will look differently. For example: Will
  it need legs? If so, how many? Will it need wheels? If so, how many? I would suggest
  that the environment and the task that we have to accomplish should be formulated
  in a way, that we can use a robot with 4 wheels. In order to keep it simple and
  focus on more interesting tasks.
* The architecture with two external controllers (external controller and backend)
  seems somewhat redundant. The only reasons we would need such an architecture
  instead of the webots controller and one external controller / backend / server are:
  * We have to, because it is a formal requirement
  * We can not use Python for the external controller. All ML code is in Python.
    So we are forced to split the python part from the controller.
  * The webots need to communicate. They are not allowed to communicate directly
    (WHY??). So we have to make them communicate via an external controller.
* Please: everybody respond on slack in a appropriate time (24h / 48h ?). Otherwise
  communication is very slow.  

#### Questions
* Can we use predefined communication protocols on top of tcp/ip?
* We should stick to the tinkerbot subset of robots. It is stated, that we should
  use a GPS sensor to determine the destination of the robot. Can we use other sensors?
  The tinkerbot subset only has a distance and a light sensor. They are not very useful.
  Verena stated, that we should use cheap and "bad" sensors to make it harder / more
  realistic? For example, can we use a cheap lidar sensor (LDS-01)?
  Can we use expensive sensors (Velodine)?
* The task is to create a robot that can go from a to b? But what will the environment
  look like? At least give us a couple of possible
  environments or stuff that we have to expect. For example: You generate 10
  possible environments and give us 3 of those environments or try to describe
  what these will look like. It would be a completely different task to build
  a robot that can clean your room vs. a robot that can go to mars. Like what
  actuators and sensors does our robot need?
* Is the target area that our robot has to reach specified by gps coordinates?
* Does our robot have to be able to work with other robots? Two different statements
  in lecture notes on isis (has to vs. optional). Do we get better marks if it can
  work with other robots / in a network? How would they cooperate? Can you give an
  example where it would be useful to have two robots? Maybe to explore the space
  faster? When one robot has reached the destination it can inform the other robot
  about the way it got there and then the other robot can get there too?
* Do we need to simulate batteries and do we have to charge the robot? Charging station?
* We should answer these Questions from the lecture slides. but there are thousands of
  possible answers (it can get very easy / very hard). How do these answers influence the
  grade?
  * Through which terrain should the robot move? <- flat and even (too easy? :D)
  * (consider your available actors)? <- just one? nothing else?
  * What should the obstacles look like? <- none?
  * (consider your available sensors)? <- all we want?
  * Should the test environment differ from the training environment? <- no?
  * Which sensors and actors should the robot use? <- all?
  * (how does your environment look like)? <- see above
  * Should the Webots controller rely entirely on the external controller or integrate
    own safety measures? <- integrate own safety measures
  * What information should the Webots controller exchange with the external
    controller? <- depends on the connection we have
  * Cope with unstable connections, communication delay and
    complete communication breakdowns <- only between robots or also between
    components of one robot?
  * Cope with “lost robots”
  * Cope with unreliable sensor data <- how should we cope with unreliable sensor
    data? What does unreliable mean?
  * The number of robots may change <- is this mandatory or optional?
  * The environment may change <- how? from sand to water? from kitchen to mars?
  * Due to “virtual robots“: simulate environmental changes
    and communication faults
* Disable visual effects in Linux in order to speed things in webots up. Do you
  have any experience on that? What is the speedup? Is it necessary?
* External Controller vs. supervisor controller? I guess we are not allowed to
  use a supervisor controller? Haha :D
* Webots regular physics behavior? No external / special physics engine? Leave all
  settings as stock (g = 9.81 and so on...)?
