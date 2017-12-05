from mazeview import MazeView

class MazeTile(object):
	
	def __init__(self, x, y, maze_dim):
		self.x = x
		self.y = y
		self.maze_dim = maze_dim
		self.connections = {}
		self.algo_data = {}
	
		# The number of entries inconnections known where
		# the keys are: N, E, S, W
		self.num_known_adjacents = 0

	def __ne__(self, other):
		if (other == None): 
			return True
		
		if((self.x == other.x) and (self.y == other.y)):
			return False
		else:
			return True

	# Currently running in adjacent mode
	def add_connection(self, direction, tile_ref):
		# if the value already exists, 
		# and is different from the tile ref, 
		# raise a value error. 
		current_val = self.connections.get(direction)
		if(current_val == None):
			self.connections[direction] = tile_ref
			self.num_known_adjacents += 1
		else:
			if(current_val != tile_ref):
				raise ValueError("Overwriting tile ref! Bad Logic!")

	def add_wall(self, direction):
		if(direction in self.connections):
			current_val = self.connections[direction]
			if(current_val is not None):
				raise ValueError("Overwriting tile ref! Bad Logic!")
		else:
			self.connections[direction] = None
			self.num_known_adjacents += 1

	# Something to clean the code when adding walls with the robot. 
	def add_wall_list(self, directions):
		for direction in directions:
			self.add_wall(direction)

	def get_num_known_adjacents(self):
		return self.num_known_adjacents	

class MazeGraph(object):
	def __init__(self, maze_dim):

		self.maze_dim = maze_dim
		self.data = []

		for x in xrange(self.maze_dim):
			for y in xrange(self.maze_dim):	
				self.data.append(MazeTile(x, y, self.maze_dim))

	def get_tile(self, x, y):
		return self.data[x * self.maze_dim + y]

# One potential "algorithm"
class ManualControl(object):
	def __init__(self, maze_dim):
		self.maze_dim = maze_dim

		# in case user is done controlling manually. 
		self.default_behavior = False

	def next_move(self, **kwargs):
		
		if(self.default_behavior):
			return 0, 0

		rotation = int(raw_input("rotation: "))
		movement = int(raw_input("movement: "))

		if(rotation == -1):
			self.default_behavior = True
			rotation = 0
			movement = 0

		return rotation, movement

class Robot_v2(object):
	def __init__(self, maze_dim):
		
		self.move_num = 1

		self.location = [0, 0]

		# to facilitate easy heading switching, 
		# we keep some helper data.
		self.heading = "N"
		self.heading_index = 0
		self.heading_list = ["N", "E", "S", "W"]

		self.maze_dim = maze_dim

		# Set the algorithm that will be used. 
		self.algo = ManualControl(maze_dim)
		self.view = MazeView(maze_dim)
		self.maze = MazeGraph(maze_dim)

		# add in all the edges. 
		self.set_maze_edge_walls()


	def set_maze_edge_walls(self):
		for i in xrange(self.maze_dim):
			current = self.maze.get_tile(i, 0)
			current.add_wall_list(["S1", "S2", "S3"])

			current = self.maze.get_tile(i, self.maze_dim - 1)
			current.add_wall_list(["N1", "N2", "N3"])

			current = self.maze.get_tile(0, i)
			current.add_wall_list(["W1", "W2", "W3"])

			current = self.maze.get_tile(self.maze_dim - 1, i)
			current.add_wall_list(["E1", "E2", "E3"])

	
	# useful helper for update maze
	def is_valid_coords(self, x, y):
		result_x = (x >= 0) and (x < self.maze_dim)
		result_y = (y >= 0) and (y < self.maze_dim)
		return (result_x and result_y)

	# Update the maze graph itself. 
	# can run in two modes - 
	# 	* immediate = tile transitions have max of
	#	  4 entries in dict (N, E, S, W)
	# 	* extended = tile transitions have max of
	# 	  12 entries in dict (N1, N2, N3, ..., W3)
	def update_graph(self, norm_sensors):
		# Readability fix
		sensors = norm_sensors	
		# View North
		x = self.location[0]
		y = self.location[1]

		# super repetitive code, but gets the job done 
		# could be improved with more flexible lookups.
		if(sensors[0] is not None):	# North
			for i in xrange(0, sensors[0]):
				current = self.maze.get_tile(x, y + i)
				next_tile = self.maze.get_tile(x, y + i + 1)
				current.add_connection("N1", next_tile)
				next_tile.add_connection("S1", current)

			if(self.is_valid_coords(x, y + sensors[0] + 1)):
				current = self.maze.get_tile(x, y + sensors[0])
				next_tile = self.maze.get_tile(x, y+sensors[0] + 1)
				current.add_wall_list(["N1", "N2", "N3"])
				next_tile.add_wall_list(["S1", "S2", "S3"])

		if(sensors[1] is not None): # East
			for i in xrange(0, sensors[1]):
				current = self.maze.get_tile(x + i, y)
				next_tile = self.maze.get_tile(x+ i + 1, y)
				current.add_connection("E1", next_tile)
				next_tile.add_connection("W1", current)

			if(self.is_valid_coords(x+sensors[1] + 1, y)):
				current = self.maze.get_tile(x + sensors[1], y)
				next_tile = self.maze.get_tile(x + sensors[1] + 1, y)
				current.add_wall_list(["E1", "E2", "E3"])
				next_tile.add_wall_list(["W1", "W2", "W3"])

		if(sensors[2] is not None): # South	
			for i in xrange(0, sensors[2]):
				current = self.maze.get_tile(x, y - i)
				next_tile = self.maze.get_tile(x, y - i - 1)
				current.add_connection("S1", next_tile)
				next_tile.add_connection("N1", current)
	
			if(self.is_valid_coords(x, y - sensors[2] - 1)):
				current = self.maze.get_tile(x, y - sensors[2])
				next_tile = self.maze.get_tile(x, y-sensors[2] - 1)
				current.add_wall_list(["S1", "S2", "S3"])
				next_tile.add_wall_list(["N1", "N2", "N3"])	

		if(sensors[3] is not None): # West
			for i in xrange(0, sensors[3]):
				current = self.maze.get_tile(x - i, y)
				next_tile = self.maze.get_tile(x - i - 1, y)
				current.add_connection("W1", next_tile)
				next_tile.add_connection("E1", current)

			if(self.is_valid_coords(x-sensors[3] - 1, y)):
				current = self.maze.get_tile(x - sensors[3], y)
				next_tile = self.maze.get_tile(x - sensors[3] - 1, y)
				current.add_wall_list(["W1", "W2", "W3"])
				next_tile.add_wall_list(["E1", "W2", "W3"])

		self.second_pass_update(norm_sensors)

	def second_pass_update(self, norm_sensors):
		# The stitching process. 
		if(self.move_num == 1): 
			# Do the special thing for the northbound tiles. 
			print("Doing special first move processing")
			pass

		# figure out the axis we're working with. 
		if((self.heading == "N") or (self.heading == "S")):
			x_min = self.location[0] - norm_sensors[3]	
			x_max = self.location[0] + norm_sensors[1]
			y = self.location[1]
			print("Processing horiz: " + str(x_min) + " to " + str(x_max))
			for i in xrange(x_max - x_min - 1):
				# stitch these together with E2 and W2
				current = self.maze.get_tile(x_min + i, y)
				next_tile = self.maze.get_tile(x_min + i + 2, y)
				current.add_connection("E2", next_tile)
				next_tile.add_connection("W2", current)

			for i in xrange(x_max - x_min - 2):
				# stitch these together with E3 and W3
				current = self.maze.get_tile(x_min + i, y)
				next_tile = self.maze.get_tile(x_min + i + 3, y)
				current.add_connection("E3", next_tile)
				next_tile.add_connection("W3", current)
		
			# in case x_max - x_min is 0, the standard
			# maze update will have taken care of it. 

			if((x_max - x_min) >= 1):
				current = self.maze.get_tile(x_max - 1, y)
				current.add_wall_list(["E2", "E3"])
				
				current = self.maze.get_tile(x_min + 1, y)
				current.add_wall_list(["W2", "W3"])

			elif((x_max - x_min) >= 2):
				current = self.maze.get_tile(x_max - 2, y)
				current.add_wall("E3")

				current = self.maze.get_tile(x_min + 2, y)
				current.add_wall("W3")
			
		else:
			y_min = self.location[1] - norm_sensors[2]
			y_max = self.location[1] + norm_sensors[0]
			x = self.location[0]
			print("Processing vert: " + str(y_min) + " to " + str(y_max))

			for i in xrange(y_max - y_min - 1):
				# stitch these together with N2 and S2
				current = self.maze.get_tile(x, y_min + i)
				next_tile = self.maze.get_tile(x, y_min + i + 2)
				current.add_connection("N2", next_tile)
				next_tile.add_connection("S2", current)

			for i in xrange(y_max - y_min - 2):
				# stitch these together with N3 and S3
				current = self.maze.get_tile(x, y_min + i)
				next_tile = self.maze.get_tile(x, y_min + i + 3)
				current.add_connection("N3", next_tile)
				next_tile.add_connection("S3", current)

			if((y_max - y_min) >= 1):
				current = self.maze.get_tile(x, y_max - 1)
				current.add_wall_list(["N2", "N3"])
				
				current = self.maze.get_tile(x, y_min + 1)
				current.add_wall_list(["S2", "S3"])
			
			if((y_max - y_min) >= 2):
				current = self.maze.get_tile(x, y_max - 2)
				current.add_wall("N3")
				
				current = self.maze.get_tile(x, y_min + 2)
				current.add_wall("S3")
	
	# Essentially a helper to properly update the 
	# maze. 
	def normalize_sensors(self, sensors):
		
		
		# There could be a better way to do this... 
		# but take the index and do weird slicing. 
		slice_lookup = [1, 0, 3, 2]
		i = slice_lookup[self.heading_index]
	
		# First order of business - append none to a fresh copy. 
		logic_sensors = list(sensors)
		view_sensors = list(sensors)

		logic_sensors.append(None)
		view_sensors.append(None)

		# Once we realized that front sensor data is useless 
		# after the first move. 
		if(self.move_num != 1):
			logic_sensors[1] = None

		norm_logic_sensors = logic_sensors[i:] + logic_sensors[:i]
		norm_view_sensors = view_sensors[i:] + view_sensors[:i]
		return norm_logic_sensors, norm_view_sensors

	# Do this first, so that update_location works. 
	def update_heading(self, rotation):
		
		self.heading_index += (rotation / 90)
		self.heading_index %= 4
		self.heading = self.heading_list[self.heading_index]

	def update_location(self, movement):
		
		if(self.heading == "E"):
			self.location[0] += movement
		elif(self.heading == "W"):
			self.location[0] -= movement
		elif(self.heading == "N"):
			self.location[1] += movement
		elif(self.heading == "S"):
			self.location[1] -= movement
		else:
			# Should raise an Error here... 
			raise ValueError("Update Location has a bad heading")

	def next_move(self, sensors):
		# The robot is responsible for cleaning the data it
		# gets before passing it to viewers and algos. 
		# The robot *is* the driver to the real world. 

		logic_sensors, view_sensors = self.normalize_sensors(sensors)
		self.update_graph(logic_sensors)

		# Pass the data necessary to render
		# info on the maze before the algo runs. 
		# (To see what the input to the algo is)
		info_to_view = {
			"graph": None,
			"heading": self.heading,
			"location": self.location,
			"normalized_sensors": view_sensors,
			"maze": self.maze
		}

		self.view.pre_algo_view(**info_to_view)
		
		# pass the graph, heading and location. 
		# Extendible. 
		info_to_algo = {
			"graph": None,
			"heading": self.heading,
			"location": self.location
		}

		rotation, movement = self.algo.next_move(**info_to_algo)
		self.update_heading(rotation)
		self.update_location(movement)
		self.move_num += 1
		return rotation, movement
