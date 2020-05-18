4th Zoom Meeting on 18.05.2020 at 11:00-12:00am

1. Standup:

    Webots / Controller:
        - Connection Webots / External Controller is working
        - Connection in External Controller is working
        - First Automation via basic Scripts
        Nextup:
        - Improve Communication / get full connection Working
        - Scripting of Webots environment

    Backend:
        - Robot control via Keyboards
        - update fake environment options
        - look into open ai gym options and improve stuff there
        - meeting on friday by backend group (ddpg vs dqn)
        - dqn as simple approach / ddpg as more complex approch
        - learn about NN input and output
        - adapt dqn to fake environment
        Nextup:
        - decide basic qualitiy plan
        - rebuiled fake environment to discrete time steps
        - train first very basic network on fake enviroment
        - randomize fake environment

2. Milestone Presentation:

    Review:
        - it is weird and hard to talk without feedback into camera
        - it helpful to have a good general plan before diving into details
        - dont use powerpoint to record the presentation

    Todo:
        - Watch three other Milestone Presentations unitl end of week
        - Fill out form and post it on Isis
        - Post one (in total) question to another group
        - Answer questions to our group

    Milestone Presentation:
        - Still have to decide on what to do present in the 2. Milestone Presentation
        - Presenters: Shanshan and Fabian

3. Rollout Plan / Next Big Things:  
    Controller:
        - Get Supervisor mode for training working
        - Randomize Webots World (using seed to be able to get a constant environment if needed)
        - Maybe start everything from Python (not from Script)  
        - Send information about the environment to backend.

    Backend:
        - Backend needs to get a randomized environment from Controller so they can train their NN
        - Implement Basic Functions / tune behaviour of fake environment / AIgym in order to run ML Algortihms
        - Get Algortihms working in fake environment (mainly focus on dqn?)
        - Mats made a Fake Lidar, so that we can train in fake environment

4. Quality Assurance  

    - Unit Tests should be written by all Programmers
    - Continous Integration needs to be setup
    - Code review via Zoom (or smth. similar)

5. Real World Robot Example:
    - Testing / Presenting the automated startup using the script

New Moderator: Jonas
New Minutetaker: Rui


Random Questions:
    - How hard is the World at the end going to be?
    There will be no environment supplied. You will have to supply an environment on your own.
    - How does GPS work?
          Just plug GPS into the extension slot.
    - Do you have a target Zone?
          Not yet. We will do this as part of the  
