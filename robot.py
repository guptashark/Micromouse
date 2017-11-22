import numpy as np

# The data structure that holds all the tiles
class MazeGraph(object):
	def __init__(self, width):
		self.width = width
		# We can index with: 
		# row * width + column
		
		self.maze = []

		i = 0
		j = 0
		while(i < self.width):

			while(j < self.width):
				self.maze.append(MazeTile(i, j))
				j = j + 1

			i = i + 1
			j = 0

	# we can change the level of info we get with verbose level 0 - whatever
	def print_info(self, verbose_level):
		i = 0
		j = 0
		while(i < self.width):

			while(j < self.width):
				self.maze[i * self.width + j].print_info(verbose_level)
				j = j + 1

			i = i + 1
			j = 0

				
	

class MazeTile(object):

	# Start off every Tile as black for init. 
	# Since the Tile is black, its map to other tiles is empty. 
	# Map to other tiles: 
	#	map key is a tuple (N/E/S/W)
	#	map value is ref to other square or None if it hits wall/edge. 
	def __init__(self, x_coord, y_coord):
		# where am I? 
		self.x_coord = x_coord
		self.y_coord = y_coord
		self.color = "B"
		self.transition = {}

	# The key is the tuple: (N/E/S/W), steps)	
	# The value is the obj reference we get from the tiles Table
	def add_transition(self, pos, tile):
		""" TODO Check to see if the key is already there. 
		If it is, return 1, or something to signify it. (later) 
		"""
		self.transition[pos] = tile

	def set_white(self):
		self.color = "W"

	def set_grey(self):
		self.color = "G"

	def get_color(self):
		return self.color

	def get_transitions(self):
		return self.transitions

	def print_info(self, verbose_level):
		
		print("[" + str(self.x_coord) + ", " + str(self.y_coord) + "]")

class Robot(object):
	def __init__(self, maze_dim):

		self.location = [0, 0]
		self.heading = 'up'
		self.maze_dim = maze_dim
		self.maze_graph = MazeGraph(maze_dim)

	def update_heading(self, current_heading, rotation):
		if(current_heading == "up"):
			if(rotation == 90):
				return "right"
			elif(rotation == -90):
				return "left"
			else:
				return "up"

		elif(current_heading == "right"):
			if(rotation == 90):
				return "down"
			elif(rotation == -90):
				return "up"
			else:
				return "right"
		
		elif(current_heading == "down"):
			if(rotation == 90): 
				return "left"
			elif(rotation == -90):
				return "right"
			else:
				return "down"
		else:
			if(rotation == 90):
				return "up"
			elif(rotation == -90):
				return "down"
			else:
				return "left"

	def update_location(self, current_location, current_heading, num_steps):
		if(current_heading == "up"):
			current_location[1] = current_location[1] + num_steps
		elif(current_heading == "right"):
			current_location[0] = current_location[0] + num_steps
		elif(current_heading == "down"):
			current_location[1] = current_location[1] - num_steps
		elif(current_heading == "left"):
			current_location[0] = current_location[0] - num_steps

		return current_location

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
		self.maze_graph.print_info(1)

		print("Sensor data: " + 
			str(sensors[0]) + " " +
			str(sensors[1]) + " " + 
			str(sensors[2]))

		print("Current position: " + str(self.location))
		print("Current heading: " + self.heading)



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

		# We're going to build a map of the maze. 
		# tiles: 
		#	-black	(unseen)
		#	-grey 	(we "saw" it with sensors)
		#	-white	(we've fully discovered it.)
		rotation = rotation_int
		movement = int(user_movement)

		self.heading = self.update_heading(self.heading, rotation)
		self.location = self.update_location(self.location, self.heading, movement)

		return rotation, movement
