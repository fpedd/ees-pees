
## Meeting on 04.05.2020
#### Agenda
* Backend Team has to work on theory behind RL and figure out a good architecture.
  * What NN should we use (maybe have a couple at the ready that we can test?).
  * Then find a concept on how to train that network. What is a good reward function?
  * Figure out a high level controller that controls the mission.
  *

#### Interesting
* Webots can be started from a script, you can options such as fast mode and
  logging to an external file, this could be interesting for automated training
*

#### Questions
* Can we use predefined communication protocols on top of tcp/ip?
* We should stick to the tinkerbot subset of robots. It is stated, that we should
  use a GPS sensor to determine the destination of the robot. Can we use other sensors?
  The tinkerbot subset only has a distance and a light sensor. They are not very useful.
  Verena stated, that we should use cheap and "bad" sensors to make it harder / more
  realistic? For example, can we use a cheap lidar sensor? Can we use expensive sensors?
* The task is to create a robot that can go from a to b? But what will the environment
  look like? At least give us a couple of possible
  environments or stuff that we have to expect. For example: You generate 10
  possible environments and give us 3 of those environments or try to descibre
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
    own safety measures? <- integrate own saftey measures
  * What information should the Webots controller exchange with the external
    controller? <- depends on the connection we have
  * Cope with unstable connections, communication delay and
    complete communication breakdowns <- only between robots or also between
    components of one robot?
  * Cope with “lost robots”
  * Cope with unreliable sensor data <- how should we cope with unreliable sensor
    data? What does unreliable mean?
  * The number of robots may change <- is this mandatory or optinal?
  * The environment may change <- how? from sand to water? from kitchen to mars?
  * Due to “virtual robots“: simulate environmental changes
    and communication faults
