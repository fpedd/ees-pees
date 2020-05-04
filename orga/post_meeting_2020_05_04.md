Protocol for 2nd Meeting on March 04 2020, 11AM
3 planning layers:
   - 1 week Plan
   - Milestone Plan
   - Project Plan
Today:
   - 1 week plan
   - Model Project simple for ease of use
   - Assignment of split tasks
Announcements:
   - Ticket System is set up in GitHub (*)
Project modelling:
   - Simple environement with the objective of reaching a goal with simple obstructions of the path
   - p. ex. requirement of no collision with obstacles, referring to it needing to be "Safe"
   - Complexity increase when more time is left p. ex. add noise to sensors
   - Layer Structure:
       - Sensor Data send to backend directly aswell as
       - Instructions sent back directly
       --> Controller only for passing sensor data and execute commands from the backend
       - Controller<->Backend interface realised with only TCP/IP
    - Sensors:
        - I/O Format to be discussed by Backend and Controller
        - Input:
            - GPS
            - Lidar (Distance)
        - Output:
            - Direction
            - Speed
        - Sensor noise: Disabled for now, maybe use it in the future with a preprocessing on the external controller p. ex.
Implementation:
   - Higher Level Python Environement for Testing -> e.g https://gym.openai.com/
   - Controller Group focusses on the TCP/IP interface
Simulation environement:
   - Using university servers for computation?
   - Random Map generation for training
   - Supervisor usage to evaluate reward function
   --> Training Automation
Ticket System
- * Notion Ticket System (Per) for better layout
1 week plan:
   - Backend Group:  Discuss plans on further procedure, requirements for the interface
   - Controller Group: First approaches for the interface
   - Quality Group:     Plan test environement
   - Next week roles: Wladimir (moderator), Per (minute taker)
Milestone Plan:
   - Get a first prototype roughly working
Project Plan:
   - Simple robot in environement with the objective of reaching a goal with simple obstructions of the path
