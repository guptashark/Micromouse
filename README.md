# Micromouse

## About

Micromouse is a program in which a robot explores a maze on its first run and then tries to find the fastest route to the center on its second run. Here is some more information on the [contest.](https://en.wikipedia.org/wiki/Micromouse) 

In this version, the rules are simple. The robot can move in any of the 4 cardinal directions at most 3 steps per move. The robot has to explore a square maze of dimensions 12x12, 14x14 or 16x16. On the first run, the score is (1/30) times the number of moves the robot makes to finish the run. The score for the second run is the number of moves the robot takes to get to the center. Sum the scores for the first and second run to get the total score. The lower the total score, the better. 


## Building
The code runs using python2. Navigate to the project directory and pick which test maze you want to run the agent on. Then, execute: **python2 testmaze.py testmaze.txt**

Another thing you can do is see the mazes themselves, which can by done by executing: **python2 showmaze.py testmaze.txt**
