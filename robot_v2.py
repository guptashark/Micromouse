

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

class MazeView(object):
	
	# maze_dim as a param makes everything easier. 	
	def __init__(self, maze_dim):
		self.maze_dim = maze_dim

	# Print before the algo runs, to see what the algo
	# is working with. 
	def pre_algo_view(self, **kwargs):
		# location and heading are basic. Always print. 
		location = kwargs["location"]
		heading = kwargs["heading"]
		normalized_sensors = kwargs["normalized_sensors"]
		maze = kwargs["maze"]

		location_output = "Location: " + str(location)
		heading_output = "Heading: " + heading
		output_1 = location_output + "\t" + heading_output

		arrow_dict = {
			"N": unichr(0x25B2),
			"E": unichr(0x25B6),
			"S": unichr(0x25BC),
			"W": unichr(0x25C0)
		}
		unicode_arrow = arrow_dict[heading]

		sensor_N = str(normalized_sensors[0])
		sensor_E = str(normalized_sensors[1])
		sensor_S = str(normalized_sensors[2])
		sensor_W = str(normalized_sensors[3])

		output_2 = "\n\t" + sensor_N + "\n" + sensor_W + "\t" + unicode_arrow + "\t" + sensor_E + "\n\t" + sensor_S

		print(output_1)
		print(output_2)

		# Now we print the maze itself. 
		current_str = ""
		for y in xrange(self.maze_dim - 1, -1, -1):
			for x in xrange(self.maze_dim):
				current = maze.get_tile(x, y)
				current_str = current_str + str(current.get_num_known_adjacents())
			print current_str
			current_str = ""


class Robot_v2(object):
	def __init__(self, maze_dim):

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
			current.add_wall("S")

			current = self.maze.get_tile(i, self.maze_dim - 1)
			current.add_wall("N")

			current = self.maze.get_tile(0, i)
			current.add_wall("W")

			current = self.maze.get_tile(self.maze_dim - 1, i)
			current.add_wall("E")

	
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
		
		# View North
		x = self.location[0]
		y = self.location[1]

		if(norm_sensors[0] is not None):	# North
			for i in xrange(0, norm_sensors[0]):
				current = self.maze.get_tile(x, y + i)
				next_tile = self.maze.get_tile(x, y + i + 1)
				current.add_connection("N", next_tile)
				next_tile.add_connection("S", current)

			if(self.is_valid_coords(x, y + norm_sensors[0] + 1)):
				current = self.maze.get_tile(x, y + norm_sensors[0])
				next_tile = self.maze.get_tile(x, y+norm_sensors[0] + 1)
				current.add_wall("N")
				next_tile.add_wall("S")

		if(norm_sensors[1] is not None): # East
			for i in xrange(0, norm_sensors[1]):
				current = self.maze.get_tile(x + i, y)
				next_tile = self.maze.get_tile(x+ i + 1, y)
				current.add_connection("E", next_tile)
				next_tile.add_connection("W", current)

			if(self.is_valid_coords(x+norm_sensors[1] + 1, y)):
				current = self.maze.get_tile(x + norm_sensors[1], y)
				next_tile = self.maze.get_tile(x + norm_sensors[1] + 1, y)
				current.add_wall("E")
				next_tile.add_wall("W")

		if(norm_sensors[2] is not None): # South	
			for i in xrange(0, norm_sensors[2]):
				current = self.maze.get_tile(x, y - i)
				next_tile = self.maze.get_tile(x, y - i - 1)
				current.add_connection("S", next_tile)
				next_tile.add_connection("N", current)
	
			if(self.is_valid_coords(x, y - norm_sensors[2] - 1)):
				current = self.maze.get_tile(x, y - norm_sensors[2])
				next_tile = self.maze.get_tile(x, y-norm_sensors[2] - 1)
				current.add_wall("S")
				next_tile.add_wall("N")	

		if(norm_sensors[3] is not None): # West
			for i in xrange(0, norm_sensors[3]):
				current = self.maze.get_tile(x - i, y)
				next_tile = self.maze.get_tile(x - i - 1, y)
				current.add_connection("W", next_tile)
				next_tile.add_connection("E", current)

			if(self.is_valid_coords(x-norm_sensors[3] - 1, y)):
				current = self.maze.get_tile(x - norm_sensors[3], y)
				next_tile = self.maze.get_tile(x - norm_sensors[3] - 1, y)
				current.add_wall("W")
				next_tile.add_wall("E")



	# Essentially a helper to properly update the 
	# maze. 
	def normalize_sensors(self, sensors):
		# There could be a better way to do this... 
		# but take the index and do weird slicing. 
		slice_lookup = [1, 0, 3, 2]
		i = slice_lookup[self.heading_index]
	
		# First order of business - append none to a fresh copy. 
		local_sensors = list(sensors)
		local_sensors.append(None)

		normalized_sensors = local_sensors[i:] + local_sensors[:i]
		return normalized_sensors

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

		normalized_sensors = self.normalize_sensors(sensors)
		self.update_graph(normalized_sensors)

		# Pass the data necessary to render
		# info on the maze before the algo runs. 
		# (To see what the input to the algo is)
		info_to_view = {
			"graph": None,
			"heading": self.heading,
			"location": self.location,
			"normalized_sensors": normalized_sensors,
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
		return rotation, movement
