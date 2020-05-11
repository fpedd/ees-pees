# Meeting 200511 Notes

## Stand-up
### Wladimir:
    past: created Prototypes (see Slack), 2 suitable, overview of Interface to External Controller
    future: 

### Jonas:
    past: client/external controller connection with fixed numbers
    future: implement conenction from external to internal -> Integration
    
### Fabi:
    past: interface to backend (with Per), working connection
    future: integrate all connections
        
### Per:
    past: Interface, fake environment, milestone presentation
    future: fake environment? / py modules

### Shanshan:
    past: tested SARSA in fake environment/ frozen lake
    future: checkout environment at git

### Rui
    past: Qlearning/SARSA 
    future: Create Environment?

### Mats
    past: fake environment/frozen Lake -> Qlearning  and other model free-agorithms 
    future: model-based algorithms

## General:
    use Notion
    make 1 week and 4 week plans by connection your tasks to the epics (milestones) and sprints
    General: how to automate the training procedure
    Next week: Mats moderator, Fabi Minute taker

## Webots/Controller:
    supervisor in Webot is premium function -> how to random initialize? -> @Wladimir -> Milestone 2

## Backend
    start with RL -> move to Safe RL
    explore different algorithms in git
    Safe: Idea: penalize Robot if close to obstalce in certain distance (e.g. 0.5m)

## Controls:
    start with absolute heading -> maybe transition later to relative (what to do with packet loss?)
    change 3d compass vector to 1d compass
