from mazeview import MazeView
from collections import deque


class MazeTile(object):
	
	# a shared ref to maze
	# to update its "knowledge" index
	maze_ref = None

	def __init__(self, x, y, maze_dim):
		self.x = x
		self.y = y
		self.maze_dim = maze_dim

		# connections for all adjacents, 
		# result val can be None
		self.connections = {}

		# Tile links for only links
		# where action can be made by robot
		# and reaches a tile. 
		self.tile_links = {}
		self.algo_data = {}
	
		# The number of entries inconnections known where
		# the keys are: N, E, S, W
		self.coverage_index = 0

	def __ne__(self, other):
		if (other == None): 
			return True
		
		if((self.x == other.x) and (self.y == other.y)):
			return False
		else:
			return True

	# To allow storing tiles in sets and dicts
	# for algos
	def __hash__(self):
		return self.maze_dim * self.x + self.y
	
	def __repr__(self):
		ret_val = "(" + str(self.x)	+ ", " + str(self.y) + ")"
		return ret_val

	# Currently running in adjacent mode
	def add_connection(self, direction, tile_ref):
		# if the value already exists, 
		# and is different from the tile ref, 
		# raise a value error. 
		current_val = self.connections.get(direction)
		if(current_val == None):
			self.connections[direction] = tile_ref
			self.tile_links[direction] = tile_ref
			self.coverage_index += 1
			MazeTile.maze_ref.increment_coverage()
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
			self.coverage_index += 1
			MazeTile.maze_ref.increment_coverage()

	# Something to clean the code when adding walls with the robot. 
	def add_wall_list(self, directions):
		for direction in directions:
			self.add_wall(direction)

	def get_coverage_index(self):
		return self.coverage_index	

	def get_connections(self):
		return self.connections

	def get_tile_links(self):
		return self.tile_links

class MazeGraph(object):
	def __init__(self, maze_dim):

		self.maze_dim = maze_dim

		# to calc how much we know about the maze. 
		# (Sum of number of actions known per tile, 
		# whether it be a wall, maze edge, etc. 
		self.raw_coverage_index = 0
		self.total_coverage = 12 * self.maze_dim ** 2

		# The tiles themselves
		self.data = []

		for x in xrange(self.maze_dim):
			for y in xrange(self.maze_dim):	
				self.data.append(MazeTile(x, y, self.maze_dim))

	def get_tile(self, x, y):
		return self.data[x * self.maze_dim + y]

	def increment_coverage(self):
		self.raw_coverage_index += 1

	def get_coverage_score(self):
		
		current_coverage = float(self.raw_coverage_index)
		complete_coverage = float(self.total_coverage)

		raw_percent = current_coverage / complete_coverage

		score = int(raw_percent * 100)
		return score

class MazeAlgorithm(object):

	def key_to_action_tuple(self, move_key, heading):
		if(move_key == "Reset"):
			return 'Reset', 'Reset'
		
		action_direction = move_key[0]
		action_steps = int(move_key[1])

		# same direction	
		if(action_direction == heading):
			return (0, action_steps)

		opposite_dict = {
			"N": "S",
			"E": "W", 
			"S": "N", 
			"W": "E"
		}

		# opposite directions
		if(opposite_dict[action_direction] == heading):
			return (0, -1 * action_steps)

		# need to make a turn, 
		# key: ("robot heading", "move direction")
		# value: rotation
		turn_dict = {
			("N", "E"): 90,
			("E", "S"): 90,
			("S", "W"): 90,
			("W", "N"): 90,

			("N", "W"): -90,
			("E", "N"): -90,
			("S", "E"): -90,
			("W", "S"): -90
		}

		rotation = turn_dict[(heading, action_direction)]
		return (rotation, action_steps)


# One potential "algorithm"
class ManualControl(MazeAlgorithm):
	def __init__(self, maze_dim):
		self.maze_dim = maze_dim

	def next_move(self, **kwargs):
		heading = kwargs["heading"]
		action = raw_input()
		ret_val = self.key_to_action_tuple(action, heading)
		return ret_val

class GreedyWalk(MazeAlgorithm):
	def __init__(self, maze_dim):
		self.maze_dim = maze_dim

	def next_move(self, **kwargs):
		
		maze = kwargs["graph"]	
		location = kwargs["location"]
		heading = kwargs["heading"]
		x = location[0]
		y = location[1]

		print (str(x) + " " + str(y))
		#print(str(x) + " " + str(y))

		current_tile = maze.get_tile(x, y)
		
		if (maze.get_coverage_score() > 75):
			print("SENDING RESET!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			return 'Reset', 'Reset'
		
		links = current_tile.get_tile_links()
		for key in links:
			destination = links[key]
			if (destination.get_coverage_index() < 12):
				return self.key_to_action_tuple(key, heading)

		#janky, fix this
		for key in links:
			destination = links[key]
			return self.key_to_action_tuple(key, heading)

class Robot_v2(object):
	def __init__(self, maze_dim):
		
		self.move_num = 1
		self.on_second_run = False
		self.dijkstra_path = None

		self.location = [0, 0]

		# to facilitate easy heading switching, 
		# we keep some helper data.
		self.heading = "N"
		self.heading_index = 0
		self.heading_list = ["N", "E", "S", "W"]

		self.maze_dim = maze_dim

		# Set the algorithm that will be used. 
	#	self.algo = ManualControl(maze_dim)
		self.algo = ManualControl(maze_dim)
		self.view = MazeView(maze_dim)
		self.maze = MazeGraph(maze_dim)

		# Give the tiles class a ref to the maze
		MazeTile.maze_ref = self.maze
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
				next_tile.add_wall_list(["E1", "E2", "E3"])

		self.second_pass_update(norm_sensors)

	def second_pass_update(self, norm_sensors):
		# The stitching process. 
		if(self.move_num == 1): 
			# Do the special thing for the northbound tiles. 
			# all vars in this block are prefixed with "fm"
			# for "first move" 
			fm_y_min = 0
			fm_y_max = norm_sensors[0]
			fm_x = 0

			for i in xrange(fm_y_max - 1):
				# stitch these together with N2 and S2
				current = self.maze.get_tile(fm_x, i)
				next_tile = self.maze.get_tile(fm_x, i + 2)
				current.add_connection("N2", next_tile)
				next_tile.add_connection("S2", current)

			for i in xrange(fm_y_max  - 2):
				# stitch these together with N3 and S3
				current = self.maze.get_tile(fm_x, i)
				next_tile = self.maze.get_tile(fm_x, i + 3)
				current.add_connection("N3", next_tile)
				next_tile.add_connection("S3", current)

			if(fm_y_max >= 1):
				current = self.maze.get_tile(fm_x, fm_y_max - 1)
				current.add_wall_list(["N2", "N3"])
				
				current = self.maze.get_tile(fm_x, 1)
				current.add_wall_list(["S2", "S3"])
			
			if(fm_y_max  >= 2):
				current = self.maze.get_tile(fm_x, fm_y_max - 2)
				current.add_wall("N3")
				
				current = self.maze.get_tile(fm_x, 2)
				current.add_wall("S3")
	
		# figure out the axis we're working with. 
		if((self.heading == "N") or (self.heading == "S")):
			x_min = self.location[0] - norm_sensors[3]	
			x_max = self.location[0] + norm_sensors[1]
			y = self.location[1]
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

			if((x_max - x_min) >= 2):
				current = self.maze.get_tile(x_max - 2, y)
				current.add_wall("E3")

				current = self.maze.get_tile(x_min + 2, y)
				current.add_wall("W3")
			
		else:
			y_min = self.location[1] - norm_sensors[2]
			y_max = self.location[1] + norm_sensors[0]
			x = self.location[0]

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

	# Should do all the reset stuff that we need to... 
	def begin_performance_run(self):
		P = self.get_shortest_path_tree()

		# the 4 center squares
		# There could be multiple paths to the center, 
		# some marginally smaller than others. 
	
		c = self.maze_dim / 2
	
		goal_tiles = []
		goal_tiles.append(self.maze.get_tile(c, c))
		goal_tiles.append(self.maze.get_tile(c, c-1))
		goal_tiles.append(self.maze.get_tile(c-1, c))
		goal_tiles.append(self.maze.get_tile(c-1, c-1))

		# list of 4 lists
		goal_directions = [[], [], [], []]

		for i in xrange(4):
			current = goal_tiles[i]
			parent = P[current][1]
			goal_directions[i].append(P[current][2])

			while(parent is not None):
				current = parent
				goal_directions[i].append(P[current][2])
				parent = P[current][1]

		# Now get the path with the shortest len... 
		# we could run a fun list sort, but this is 
		# honestly easier
		min_dist = 2000
		shortest_index = None
		for i in xrange(4):
			if(len(goal_directions[i]) < min_dist):
				min_dist = len(goal_directions[i])
				shortest_index = i

		shortest_path = goal_directions[shortest_index]
		shortest_path.pop()
		shortest_path.reverse()

		self.on_second_run = True
		self.dijkstra_path = shortest_path
	
	# Shortest path algo using dijkstra on second run. 
	def get_shortest_path_tree(self):

		start_tile = self.maze.get_tile(0, 0)

		# set of nodes. 
		Q = set()

		# dict where: 
		# key: MazeTile 
		# value: [distance, prev_tile, edge]
		P = {}
		
		D = deque()
		D.append(start_tile)
	
		# Construct the set Q. 
		while (len(D) > 0): 
			current = D.popleft()
			connections = current.get_tile_links()
			for action in connections:
				destination = connections[action]
				if(destination not in Q):
					D.append(destination)

			Q.add(current)
			P[current] = [2000, None, None]

		P[start_tile] = [0, None, None]

		# Run Dijkstras on Q
		while(len(Q) > 0):
			min_so_far = 2000
			min_tile = None

			for tile in Q:
				dist = P[tile][0]
				if(dist < min_so_far):
					min_so_far = dist
					min_tile = tile

			u = min_tile
			u_dist = P[u][0]

			Q.remove(u)
			u_connections = u.get_connections()

			for action in u_connections:
				
				u_destination = u_connections[action]
				if(u_destination is not None):
					alt = u_dist + 1
					if (alt < P[u_destination][0]):
						P[u_destination] = [alt, u, action]
		return P
	
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
		if(rotation == 'Reset'):
			self.heading = "N"
			self.heading_index = 0
			return 
		
		self.heading_index += (rotation / 90)
		self.heading_index %= 4
		self.heading = self.heading_list[self.heading_index]

	def update_location(self, movement):
		if(movement == 'Reset'):
			self.location = [0, 0]
			return
		
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
		
		if(self.on_second_run):
			# Do the calculation for the second run move logic here. 	
			action = self.dijkstra_path.pop(0)
			# now turn it into the action
			rotation, movement = self.algo.key_to_action_tuple(action, self.heading)

			self.update_heading(rotation)
			# Don't care much about updating the location - should be perfect
	
			return rotation, movement
		
		# The robot is responsible for cleaning the data it
		# gets before passing it to viewers and algos. 
		# The robot *is* the driver to the real world. 

		# sensors for actual computation use
		# vs what user sees to ensure robot sees correctly
		logic_sensors, view_sensors = self.normalize_sensors(sensors)
		self.update_graph(logic_sensors)

		coverage_score = self.maze.get_coverage_score()
		print(coverage_score)
		# Pass the data necessary to render
		# info on the maze before the algo runs. 
		# (To see what the input to the algo is)
		info_to_view = {
			"maze": self.maze,
			"heading": self.heading,
			"location": self.location,
			"coverage_score": coverage_score,
			"normalized_sensors": view_sensors
		}
	
		"""	
		if(SETTINGS_VISUAL_ON):
			self.view.pre_algo_view(**info_to_view)
		"""
		# pass the graph, heading and location. 
		# Extendible. 
		info_to_algo = {
			"graph": self.maze,
			"heading": self.heading,
			"location": self.location
		}

		rotation, movement = self.algo.next_move(**info_to_algo)

		self.update_heading(rotation)
		self.update_location(movement)
		self.move_num += 1
		
		if(rotation == 'Reset' and movement == 'Reset'):
			self.begin_performance_run()

		return rotation, movement
