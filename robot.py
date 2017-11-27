import numpy as np
from IPython import embed

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
				self.maze[(x, y)] = MazeTile(x, y, width)
				y = y + 1

			x = x  + 1
			y = 0

		# it makes sense for the MazeGraph to automatically set the edges
		# of the maze to "None" transitions. 
		
		# top row (northmost tiles) 
		x = 0
		y = self.width - 1
		while(x < self.width):
			self.maze[(x, y)].add_transition("N", None)
			x = x + 1

		# bottom row (southmost tiles) 
		x = 0
		y = 0
		while(x < self.width):
			self.maze[(x, y)].add_transition("S", None)
			x = x + 1

		# left column (Westmost tiles) 
		x = 0 
		y = 0
		while(y < self.width):
			self.maze[(x, y)].add_transition("W", None)
			y = y + 1

		# right column (Eastmost tiles)
		x = self.width - 1
		y = 0
		while(y < self.width):
			self.maze[(x, y)].add_transition("E", None)
			y = y + 1


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
					if(connections["E"] is not None):
						to_print_str = to_print_str + "-"
				else:
					to_print_str = to_print_str + " "

				if("S" in connections):
					if(connections["S"] is not None):
						bottom_str = bottom_str + "| "
				else:
					bottom_str = bottom_str + "  "


				x = x + 1

			y = y - 1
			x = 0

			print(to_print_str)
			print(bottom_str)

	def print_knowledge_index(self):
		y = self.width - 1
		x = 0

		while(y >= 0 ):

			to_print_str = ""

			while(x < self.width):
				to_print_str = to_print_str + str(self.maze[(x, y)].get_knowledge_index())
				x = x + 1

			y = y - 1
			x = 0

			print(to_print_str)


	def print_sqr_distances(self):
		y = self.width - 1
		x = 0

		while(y >= 0 ):

			to_print_str = ""

			while(x < self.width):
				to_print_str = to_print_str + str(self.maze[(x, y)].get_distance()) + "\t"
				x = x + 1

			y = y - 1
			x = 0

			print(to_print_str)



			
	def mark_seen(self, x_coord, y_coord):
		self.maze[(x_coord, y_coord)].set_grey()

	def get_tile_ref(self, x_coord, y_coord):
		return self.maze[(x_coord, y_coord)]


class MazeTile(object):
	# Start off every Tile as black for init. 
	# Since the Tile is black, its map to other tiles is empty. 
	# give each tile the knowledge of the maze dim so it can calculate
	# how far it is from the closest center tile.
	# Map to other tiles: 
	#	map key is a tuple (N/E/S/W)
	#	map value is ref to other square or None if it hits wall/edge. 
	def __init__(self, x_coord, y_coord, width):
		# where am I? 
		self.x_coord = x_coord
		self.y_coord = y_coord
		self.width = width
		self.color = "B"
		# number that indicates how many sides we know - 
		# 0 is we know nothing, 4 is we know every side. 
		self.knowledge_index = 0
		# starts off empty. If there is a wall, transition["N"] = None. 
		# if not, transition["N"] = tile. This way, things are well defined.
		self.transition = {}
		
		closest_center_y_val = 0
		closest_center_x_val = 0

		if(y_coord >= self.width / 2):
			closest_center_y_val = self.width / 2
		else:
			closest_center_y_val = (self.width / 2) - 1
	
		if(x_coord >= self.width / 2):
			closest_center_x_val = self.width / 2
		else:
			closest_center_x_val = (self.width / 2) - 1

		# now find the euclidean distance

		x_sqr_dist = (closest_center_x_val - x_coord)**2
		y_sqr_dist = (closest_center_y_val - y_coord)**2

		self.distance_from_center = x_sqr_dist + y_sqr_dist

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
		if(direction not in self.transition):
			self.transition[direction] = tile
			self.knowledge_index = self.knowledge_index + 1

	def set_white(self):
		self.color = "W"

	def set_grey(self):
		self.color = "G"

	def get_color(self):
		return self.color

	def get_transitions(self):
		return self.transition

	def get_knowledge_index(self):
		return self.knowledge_index

	def print_info(self, verbose_level):
		
		print("[" + str(self.x_coord) + ", " + str(self.y_coord) + "]")

	def get_distance(self):
		return self.distance_from_center


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
	# We also introduce connections, so that we can build a small 
	# graph of where the robot knows it can go. 
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
			
			i = 0
			while(i < normalized_sensors[0]):
				current = self.maze_graph.get_tile_ref(x, y + i)
				next_tile = self.maze_graph.get_tile_ref(x, y + i + 1)
				# link them together
				current.add_transition("N", next_tile)
				next_tile.add_transition("S", current)
				i = i + 1
			
		# seen east
		if(normalized_sensors[1] != None):
			i = 1
			while(i <= normalized_sensors[1]):
				self.maze_graph.mark_seen(x + i, y)
				i = i + 1

			i = 0
			while(i < normalized_sensors[1]):
				current = self.maze_graph.get_tile_ref(x + i, y)
				next_tile = self.maze_graph.get_tile_ref(x + i + 1, y)
				# link them together
				current.add_transition("E", next_tile)
				next_tile.add_transition("W", current)
				i = i + 1


		# seen south
		if(normalized_sensors[2] != None):
			i = 1
			while(i <= normalized_sensors[2]):
				self.maze_graph.mark_seen(x, y - i)
				i = i + 1

			
			i = 0
			while(i < normalized_sensors[2]):
				current = self.maze_graph.get_tile_ref(x -i, y-i)
				next_tile = self.maze_graph.get_tile_ref(x, y - i - 1)
				# link them together
				current.add_transition("S", next_tile)
				next_tile.add_transition("N", current)
				i = i + 1



		# seen west
		if(normalized_sensors[3] != None):
			i = 1
			while(i <= normalized_sensors[3]):
				self.maze_graph.mark_seen(x - i, y)
				i = i + 1

	
			i = 0
			while(i < normalized_sensors[3]):
				current = self.maze_graph.get_tile_ref(x - i, y)
				next_tile = self.maze_graph.get_tile_ref(x - i - 1, y)
				# link them together
				current.add_transition("E", next_tile)
				next_tile.add_transition("W", current)
				i = i + 1

	

	def decide_move(self):
		""" This function is called during "next_move". At this point, 
		the maze has been updated so the robot can figure out where to
		go next. 

		Our algorithm for deciding on a direction should depend on two 
		goals: 
			1 - getting closer to the center
			2 - exploring things that are unexplored. 

		We'll have a parameter that changes the influece of the two goals- 
		In the beginning, the robot will want to explore more, and later
		on, it'll want to get closer to the center. Since mazes are tricky, 
		and could be adversarial, it's best to keep exploring, even after
		finding the center. 

		We may also want to add in more information about the tiles themselves. 
		For instance, if we see north 0 spaces and we're on tile (3, 4), then 
		we can fill in information on tile (3, 5) - it's south space is None. 
		Then, we're building the map faster and can even write in that we know
		1/4 data points about the tile (3, 4). The only issue is, that we'll start
		collecting too much info for us to have printed out every time. We can 
		see log files, and perhaps start inspecting things. 

		So now, we use ipython embed.

		How can we integrate the idea that we know how much we know of each 
		node into whether we want to go to it? Also, there is a unique idea: 
		We could have two metrics in a node to signify how far away it is 
		from the center. 1 is the square of the euclidean distance, the other
		is the number of steps that particular square is from a center square. 

		Right now, it's best to figure out how close each space is to the 
		center as a measure of it's worth. 
		"""	
	
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

		# print("Sensor data: " + 
		#	str(sensors[0]) + " " +
		#	str(sensors[1]) + " " + 
		#	str(sensors[2]))

		# we need to normalize sensor data to N, E, S, W so that
		# we can then update the mazeview. 
		normalized_sensor_data = self.normalize_sensor_data(sensors, self.heading)

		print("Normalized sensor data: " + str(normalized_sensor_data))
		print("Current position: " + str(self.location))
		print("Current heading: " + self.heading)

		embed()

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

		# we can update those values, since we're currently assuming 
		self.heading = self.update_heading(self.heading, rotation)
		self.location = self.update_location(self.location, self.heading, movement)

		return rotation, movement
