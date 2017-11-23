import numpy as np

# The data structure that holds all the tiles
class MazeGraph(object):
	def __init__(self, width):
		self.width = width
		# We can index with: 
		# row * width + column
	
		# honestly... a dictionary works better, and is probably just as fast. 	
		# we can change implementations later. 
		self.maze = {}

		x = 0
		y = 0
		while(x < self.width):

			while(y < self.width):
				self.maze[(x, y)] = MazeTile(x, y)
				y = y + 1

			x = x  + 1
			y = 0

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

	# just get the colors from all the thingies and print them. 
	# We're adding in our view of transitions now too. 
	def print_maze_view(self):

		# To see the transition, it suffices to start from the top, and build 
		# two strings. One is the row with the tiles, and spaces between them
		# (dashes indicate connection) and then another string, 
		# with staffs to indicate vertical connection. If the connection is 
		# unknown, don't print anything. If the connection is None, don't print
		#, and if the connection exists, then print the dash or staff. 
		# since we're going from top to top right, then down, always look at the 
		# right for a connection, and down. Then, we'll get a full graph. 

		y = self.width - 1
		x = 0

		while(y >= 0 ):

			to_print_str = ""
			bottom_str = ""

			while(x < self.width):
				to_print_str = to_print_str + self.maze[(x, y)].get_color()
				connections = self.maze[(x, y)].get_transitions()
				# check if "R" is in connections and if "S" is in connections
				if("E" in connections):
					to_print_str = to_print_str + "-"
				else:
					to_print_str = to_print_str + " "

				if("S" in connections):
					bottom_str = bottom_str + "| "
				else:
					bottom_str = bottom_str + "  "


				x = x + 1

			y = y - 1
			x = 0

			print(to_print_str)
			print(bottom_str)
			
	def mark_seen(self, x_coord, y_coord):
		self.maze[(x_coord, y_coord)].set_grey()



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

	# The key is the direction (N, E, S, W)
	# The value is the obj reference we get from the MazeTile Table
	# None if there is a wall, 
	# The reference itself if we can get there from the current tile. 
	# Don't need to make the extra branches to signify where all we 
	# can go in one move, a later algo can take care of that. 
	# To minimize memory footprint, we have a simpler graph with less
	# , but still fully representative connections. 
	def add_transition(self, direction, tile):
		""" TODO Check to see if the key is already there. 
		If it is, return 1, or something to signify it. (later) 
		"""
		self.transition[direction] = tile

	def set_white(self):
		self.color = "W"

	def set_grey(self):
		self.color = "G"

	def get_color(self):
		return self.color

	def get_transitions(self):
		return self.transition

	def print_info(self, verbose_level):
		
		print("[" + str(self.x_coord) + ", " + str(self.y_coord) + "]")


class Robot(object):
	def __init__(self, maze_dim):

		self.location = [0, 0]
		self.heading = 'up'
		self.maze_dim = maze_dim
		self.maze_graph = MazeGraph(maze_dim)

	# puts None for the direction opposite the robot. 
	def normalize_sensor_data(self, sensor_data, current_heading): 
		# nd stands for normalized data, sd for sensor data
		nd = [None, None, None, None]
		sd = sensor_data
		if(current_heading == "up"):
			nd[0] = sd[1]
			nd[1] = sd[2]
			nd[2] = None
			nd[3] = sd[0]
		elif(current_heading == "right"):
			nd[0] = sd[0]
			nd[1] = sd[1]
			nd[2] = sd[2]
			nd[3] = None
		elif(current_heading == "down"):
			nd[0] = None
			nd[1] = sd[0]
			nd[2] = sd[1]
			nd[3] = sd[2]
		else:
			nd[0] = sd[2]
			nd[1] = None
			nd[2] = sd[0]
			nd[3] = sd[1]

		return nd


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

	# Here we figure out where all we can see using normalized sensor values
	# and mark them accordingly as seen (and later fully computed)
	def update_maze_map(self, normalized_sensors):
		
		# current space
		x = self.location[0]
		y = self.location[1]

		# seen north
		if(normalized_sensors[0] != None):
			i = 1
			while(i <= normalized_sensors[0]):
				self.maze_graph.mark_seen(x, y + i)
				i = i + 1

		# seen east
		if(normalized_sensors[1] != None):
			i = 1
			while(i <= normalized_sensors[1]):
				self.maze_graph.mark_seen(x + i, y)
				i = i + 1

		# seen south
		if(normalized_sensors[2] != None):
			i = 1
			while(i <= normalized_sensors[2]):
				self.maze_graph.mark_seen(x, y - i)
				i = i + 1

		# seen west
		if(normalized_sensors[3] != None):
			i = 1
			while(i <= normalized_sensors[3]):
				self.maze_graph.mark_seen(x - i, y)
				i = i + 1
		
	
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

		# we need to normalize sensor data to N, E, S, W so that
		# we can then update the mazeview. 

		normalized_sensor_data = self.normalize_sensor_data(sensors, self.heading)
		print("Normalized sensor data: " + str(normalized_sensor_data))

		print("Current position: " + str(self.location))
		print("Current heading: " + self.heading)

		self.update_maze_map(normalized_sensor_data)

		self.maze_graph.print_maze_view()

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
