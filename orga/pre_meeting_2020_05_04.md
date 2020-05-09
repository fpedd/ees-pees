2nd Zoom Meeting on 04.05.2020 at 11:00-12:00hrs s.t.
* Zoom Meeting:
   * Time: May 4, 2020 11:00 AM Amsterdam, Berlin, Rome, Stockholm, Vienna
   * Join Zoom Meeting https://tu-berlin.zoom.us/j/4299820482?pwd=ZDVLZ0NmMVhwaGppM1F2MjZWMS9YQT09
   * Meeting ID: 429 982 0482
   * Password: 43208638


* General :
   * Let's get everybody working. We all need to have something to do. Time is short. We will need to have something to present in 2 Weeks.
   * Get a General Plan Ready. Use 3 Layers / Types of Plans:
      * One Week Plan -> a very concrete Plan for every week
      * Next Milestone Presentation Plan -> a Plan from Milestone Presentation to Milestone Presentation
      * Hole Project Plan -> What do we want to build / achieve, what do we have to build / achieve? What is our overall Goal? What should “it” look like in the end?
   * Figure out what our 3 Plans look like at the end of the meeting.
   * Please: everybody respond on Slack in an appropriate time (24h / 48h ?). Otherwise communication is very slow.
   * Ticketing System on Github.
   * Maybe, to make things easier, simpler and more accessible, we should narrow down our project to a real world application. That would help to "very naturally" clear up a lot of questions now and in the future. For example: We are building a kitchen cleaning robot that works in kitchens. Or: We are building a drug delivery robot that delivers drugs through a city? Or something else. This way we can all naturally answer many questions ourselves and do not have to constantly figure out what is plausible and what is not.
   * Let's split into 3 main Groups:
      * Controller Group: Jonas, Wladimir, Fabian
      * Backend Group: Shanshan, Rui, Mats, Per
      * Quality Group: Shanshan, Rui (only Master Students?!)


* Controller Group:
   * Build a Robot (-familiy) in Webots
      * Select Sensors
      * Select Actuators
      * Select Shape and Form
      * Build Webots Controller that can interface with External Controller / Basic Logic
   * Get Worlds / Environments setup that we can train the Robots in. What should those Environments look like? How large should they be? What obstacles / other Actors should they contain?  
   * Get a Communication Protocol Standard defined. We need one between Webots Controller <-> External Controller and External Controller <-> Backend. Build wrapper Functions / Library for use in Python and C, so that the Backend Team can use these Functions to communicate (they should have a clean interface to work with). Also important: Make sure Interface is “clean”, i.e. gives real separation between layers. That way we can all work more or less independently on each layer.
   * Find a way to automate training / testing for the RL part. Maybe use scripts / supervisor controllers in Webots / Webots Fast Simulation Mode etc. This is needed so that we can train the NN from the Backend Team. Look into the Supervisor Controller to move the robot to desired points -> could help make training simpler.
   * Random:         
      * Webots can be started from a script, you can options such as fast mode and logging to an external file, this could be interesting for automated training
      * Should we use spaces or tabs in C? Webots examples use 1 space (WTF)?
      * Lets completely stick to c code for all controller stuff (webots and external). We all know c better than c++. All examples and apis in webots are (under the hood) written in c.


* Backend Group:
   * Has to work on the theory behind RL and figure out a good (family of) architecture(s) for our robot and its task.
   * Find a NN that is sufficient for what we need (maybe have a couple at the ready so that we can test and compare them?)
   * Find a Training / Reward function and a training Algorithm / training approach that fits our needs
   * Figure out a “mission concept” that our NN needs to represent in order for the robot to complete its task. How should the robot move through the world? Should it follow any patterns? What speed should it go at? etc...
   * What is the Input Data? What sensor data should be available and in what form should it be in?
   * What is the Output Data? How should the Backend / NN control the robot?
   * It might make sense to use the External Controller as an abstraction layer. This way the NN can work with “more dense” and higher quality data? For example: Instead of a video feed, use an algorithm in the controller to extract depth information from the image and only transmit that. Also: Instead of directly controlling the motors the NN could just command a direction and a speed that the robot should go: For example 170° at 10kph. The External Controller will then translate that into motor commands. Or maybe go even one level above that: The NN should only output to which coordinate to go next to. The External Controller will then make sure that the robot actually goes there? Etc…
   * Maybe have a look at SLAM (simultaneous localization and mapping). This is basically what we need to do https://lmgtfy.com/?q=simultaneous+localization+and+mapping+reinforcement+learning


* Quality Group:
   * Functional quality assurance:
      * Look into ways to formally verify NN and RL.
      * You are in charge of making sure that the robot, after it has been trained and the network is “finished”, acitally meets (the not yet defined) safety requirements, i.e. does not kill humans in order to get from a to b and so on
   * Non Functional quality assurance:
      * Code and Architecture is clean, modules can easy be exchanged and layers are nicely separated
      * Everything is well documented


* All:
   * What is a good communication protocol for between the layers? That depends on the connection, the sensors, and where the information is encoded / decoded. (example Video: maybe don't transmit video data. Use local algorithms to extract depth / distance information locally?)
   * Where should the safety happen? In the NN / Backend? Or in the controller? Or both?
   * Depending on the environment our robot will look differently. For example: Will it need legs? If so, how many? Will it need wheels? If so, how many? I would suggest that the environment and the task that we have to accomplish should be formulated in a way, that we can use a robot with 4 wheels. In order to keep it simple and focus on more interesting tasks.
   * The architecture with two external controllers (external controller and backend) seems somewhat redundant. The only reasons we would need such an architecture instead of the webots controller and one external controller / backend / server are:
      * We have to, because it is a formal requirement
      * We can not use Python for the external controller. All ML code is in Python. So we are forced to split the python part from the controller.
      * The webots need to communicate. They are not allowed to communicate directly (WHY??). So we have to make them communicate via an external controller.


* Questions (mostly to Willie, but also to the Group):
   * Can we use predefined communication protocols on top of tcp/ip?
   * We should stick to the tinkerbot subset of robots. It is stated that we should use a GPS sensor to determine the destination of the robot. Can we use other sensors? The tinkerbot subset only has a distance and a light sensor. They are not very useful. Verena stated that we should use cheap and "bad" sensors to make it harder / more realistic? For example, can we use a cheap lidar sensor (LDS-01)? Can we use expensive sensors (Velodine)?
   * The task is to create a robot that can go from a to b? But what will the environment look like? At least give us a couple of possible environments or stuff that we have to expect. For example: You generate 10 possible environments and give us 3 of those environments or try to describe what these will look like. It would be a completely different task to build a robot that can clean your room vs. a robot that can go to mars. Like what actuators and sensors does our robot need?
   * Where does our robot get the Target GPS Coordinates from?
   * Does our robot have to be able to work with other robots? Two different statements in lecture notes on isis (has to vs. optional). Do we get better marks if it can work with other robots / in a network? How would they cooperate? Can you give an example where it would be useful to have two robots? Maybe to explore space faster? When one robot has reached the destination it can inform the other robot about the way it got there and then the other robot can get there too?
   * Do we need to simulate batteries and do we have to charge the robot? Charging station?
   * We should answer these Questions from the lecture slides. but there are thousands of possible answers (it can get very easy / very hard). How do these answers influence the grade?
      * Through which terrain should the robot move? <- flat and even (too easy? :D)
      * (consider your available actors)? <- just one? No actors at all?
      * What should the obstacles look like? <- none?
      * (consider your available sensors)? <- all we want?
      * Should the test environment differ from the training environment? <- no?
      * Which sensors and actors should the robot use? <- all?
      * (how does your environment look like)? <- see above
      * Should the Webots controller rely entirely on the external controller or integrate its own safety measures? <- integrate own safety measures
      * What information should the Webots controller exchange with the external controller? <- depends on the connection we have
      * Cope with unstable connections, communication delay and complete communication breakdowns <- only between robots or also between components of one robot? What does unstable mean?
      * Cope with “lost robots” <- What do you mean by lost?
      * Cope with unreliable sensor data <- How should we cope with unreliable sensor data? What does unreliable mean? Maybe Checksums (for example CRC) and retransmission if failure? Handshaking?
      * The number of robots may change <- Is this mandatory or optional?
      * The environment may change <- how? from sand to water? from kitchen to mars?
      * Due to “virtual robots“: simulate environmental changes and communication faults
   * Disable visual effects in Linux in order to speed things in webots up. Do you have any experience on that? What is the speedup? Is it necessary?
   * External Controller vs. supervisor controller? Can we use a supervisor controller?
   * Webots regular physics behavior? No external / special physics engine? Leave all settings as stock (g = 9.81 and so on...)?
