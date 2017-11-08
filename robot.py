import numpy as np

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim
	print("INIT WAS CALLED ON ROBOT")

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''

	# We're going to manually control the robot for now. 

	print("Sensor data: " + 
			str(sensors[0]) + " " +
			str(sensors[1]) + " " + 
			str(sensors[2]))

	user_rotation = raw_input("Rotate (L/N/R): ")
	user_movement = raw_input("Movement [-3 <= m <= 3]: ")

	rotation_int = 0

	if(user_rotation == "L"):
		rotation_int = -90
	elif(user_rotation == "N"):
		rotation_int = 0
	elif(user_rotation == "R"):
		rotation_int = 90
	else:
		print("Invalid rotation. Passing 0.")


        rotation = rotation_int
        movement = int(user_movement)

        return rotation, movement
