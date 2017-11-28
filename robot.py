import numpy as np

# comment out the os... we don't need it than for visualization
import os
from collections import deque

# comment out the embed, we don't need it except for debugging. 
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
	def print_maze_view(self, robot_location):

		# To see the transitions, it suffices to start from the top, and build 
		# two strings. One is the row with the tiles, and spaces between them
		# (dashes indicate connection) and then another string, 
		# with staffs to indicate vertical connection. If the connection is 
		# unknown, don't print anything. If the connection is None, don't print
		#, and if the connection exists, then print the dash or staff. 
		# since we're going from top to top right, then down, always look at the 
		# right for a connection, and down. Then, we'll get a full graph. 

		# also, a nice block to see where exactly the robot is. 

		y = self.width - 1
		x = 0

		alt_table = ["?", "/", "X", "+", "O"]
		while(y >= 0 ):

			# add this in to make it easier to see which row/col we're in. 
			to_print_str = str(y) + "\t"
			bottom_str = "\t"

			while(x < self.width):
				if([x, y] == robot_location):
					to_print_str = to_print_str + unichr(0x2588)
				else:
					knowledge_index = self.maze[(x, y)].get_knowledge_index()
					to_print_str = to_print_str + alt_table[knowledge_index]
				connections = self.maze[(x, y)].get_transitions()
				# check if "R" is in connections and if "S" is in connections
				if("E" in connections):
					if(connections["E"] is not None):
						to_print_str = to_print_str + "-"
					else:
						to_print_str = to_print_str + " " 
				else:
					to_print_str = to_print_str + " "

				if("S" in connections):
					if(connections["S"] is not None):
						bottom_str = bottom_str + "| "
					else:
						bottom_str = bottom_str + "  "
				else:
					bottom_str = bottom_str + "  "
				x = x + 1
			y = y - 1
			x = 0

			print(to_print_str)
			print(bottom_str)

		# print bottom numbers to see columns - modulo 10
		axis_str = "\t"
		str_iter = 0
		while(str_iter < self.width):
			axis_str = axis_str + str(str_iter % 10) + " " 
			str_iter = str_iter + 1
		print axis_str

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

	def get_tile_ref(self, x_coord, y_coord):
		return self.maze[(x_coord, y_coord)]

	# a useful metric to know how well we're doing at exploring the maze
	def get_completion_index(self):
		
		raw_knowledge_score = 0
		x = 0
		y = 0
		while(x < self.width):
			y = 0
			while(y < self.width):
				tile_score = self.maze[(x, y)].get_knowledge_index()
				raw_knowledge_score = raw_knowledge_score + tile_score
				y = y + 1
			x = x + 1

		dec_val = float(raw_knowledge_score) / (float(self.width ** 2) * 4)
		percent_val = int(dec_val * 100)
		return percent_val

	# Now gives you two waypoints to pick from. 	
	def get_next_waypoint(self):
		
		# min_1 is min distance 1
		min_1 = 128	# bigger than any possible distance. 
		waypoint_1 = None

		min_2 = 129
		waypoint_2 = None

		# instead of finding one tile, find the best 2 tiles. If tile 2 is sufficiently closer, 
		# we may end up going there instead - especially since some tiles have the same distances. 

		x = 0
		while(x < self.width):

			y = 0
			while(y < self.width):
				
				# need to make sure: 
				# - is connected
				# - has knowledge less than 4
				# - has distance less than min. 

				current = self.maze[(x, y)]
				curr_connected = current.is_connected()
				curr_distance = current.get_distance()
				curr_knowledge = current.get_knowledge_index()

	#			print(str(current.x_coord) + " " + str(current.y_coord) + 
	#				str(curr_connected) + " " + str(curr_distance) + " " + str(curr_knowledge))

				#if(curr_connected and (curr_distance <= min_distance_so_far) and (curr_knowledge < 4)):
				if(curr_connected and (curr_knowledge < 4)):
					
					# better than both 
					if(curr_distance <= min_1):
						min_2 = min_1
						min_1 = curr_distance
						waypoint_2 = waypoint_1
						waypoint_1 = current
					elif(curr_distance <= min_2):
						min_2 = curr_distance
						waypoint_2 = current

				y = y + 1
			x = x + 1

		return [waypoint_1, waypoint_2]

	# current is the tile ref to the current location
	# waypoint is the tile ref to the waypoint  
	def get_directions_to_waypoint(self, start_point, waypoint):

		# Seems like a bad fix... but could work, right? 	
		if(waypoint == None):
			empty_list = []
			return empty_list
				
		# store the tile distance from current, 
		# and a ref to the tile that preceeds it. 
		# (So we can build our path)

		#current_distance = 0
		#not_found = True

		# fully discovered tiles
		# key: (x, y)
		# value: tile_ref to prevoius tile
		discovered = {}

		# queued up tiles to explore
		# tuple is ref to tile and ref to tile that led to it. 
		to_examine = deque('')
		to_examine.append((start_point, None))

		# sample input once a vertex is processed
		#	discovered[current.get_tuple()] = (0, None)

		# I really hate this ridiculously nested if statement
		# Prolly change it to a nice linear if elif elif etc. 
		while(True):
			cur_tup= to_examine.popleft()
			current = cur_tup[0]
			if(current is not None): 	
				if(current.tuple() not in discovered):
					if(current != waypoint):
						to_examine.append((current.transition.get("N"), current))
						to_examine.append((current.transition.get("E"), current))
						to_examine.append((current.transition.get("S"), current))
						to_examine.append((current.transition.get("W"), current))

						discovered[current.tuple()] = cur_tup[1]

		#				current_distance = current_distance + 1
					else:
						# we found the waypoint! 
						# build the list of like, cur_tup[1]'s and stuff. 

						reverse_path = [current]
						current = cur_tup[1]
							
						while(current != start_point):
							reverse_path.append(current)
							current = discovered[current.tuple()]

						return reverse_path

	



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
		# number that indicates how many sides we know - 
		# 0 is we know nothing, 4 is we know every side. 
		self.knowledge_index = 0
		# starts off empty. If there is a wall, transition["N"] = None. 
		# if not, transition["N"] = tile. This way, things are well defined.
		self.transition = {}

		self.connected = False
		
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

	def get_coords_as_str(self):
		return "[" + str(self.x_coord) + ", " + str(self.y_coord) + "]"

	def get_tuple(self):
		return (self.x_coord, self.y_coord)

	def tuple(self):
		return (self.x_coord, self.y_coord)

	def print_transitions(self):
		for i in self.transition: 
			if(self.transition[i] is None):
				print(i + ": None")
			else: 
				print(i + ": " + self.transition[i].get_coords_as_str())

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

	def get_transitions(self):
		return self.transition

	def get_knowledge_index(self):
		return self.knowledge_index

	def get_distance(self):
		return self.distance_from_center

	def set_connected(self):
		self.connected = True

	def is_connected(self):
		return self.connected


class Robot(object):
	def __init__(self, maze_dim):

		self.location = [0, 0]
		self.heading = 'up'
		self.maze_dim = maze_dim
		self.maze_graph = MazeGraph(maze_dim)
		self.num_moves = 0
		start_square = self.maze_graph.get_tile_ref(0, 0)
		start_square.set_connected()

		# for recording maze_knowledge
		self.file = open("performance_metrics/width-12.txt", 'w')

	def reset_for_run_2(self):
		self.location = [0, 0]
		self.heading = 'up'
		self.num_moves = 0
		self.file.close()
		

	# for debugging in embedded mode: 
	def get_tile_info(self, x, y):
		tile = self.maze_graph.get_tile_ref(x, y)
		print(tile.x_coord)
		print(tile.y_coord)
		tile.print_transitions()

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
		elif(current_heading == "left"):
			nd[0] = sd[2]
			nd[1] = None
			nd[2] = sd[0]
			nd[3] = sd[1]
		else:
			print("ERROR ERROR ERROR - unrecognized heading!")

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


	# loc_A, and loc_B are tuples that indicate a tiles perceived location. 
	# if the second tile is in the maze (the first is guaranteed) then the 
	# fn will join them using the direction parameter. The direction param
	# is the direction in which a robot on loc_A would travel to get to 
	# loc_B. This function is essentially a helper for update maze map
	def join_by_wall(self, loc_A, loc_B, direction):
		if(loc_B[0] >= self.maze_dim):
			return

		if(loc_B[1] >= self.maze_dim):
			return

		if(loc_B[0] < 0):
			return

		if(loc_B[1] < 0):
			return

		# at this point, it's guaranteed that we're not on an edge. 	
		opposite_dict = {
			"N": "S",
			"E": "W",
			"S": "N",
			"W": "E"
		}

		current = self.maze_graph.get_tile_ref(loc_A[0], loc_A[1])
		next_tile = self.maze_graph.get_tile_ref(loc_B[0], loc_B[1])

		current.add_transition(direction, None)
		next_tile.add_transition(opposite_dict[direction], None)
		
	# Here we figure out where all we can see using normalized sensor values
	# and mark them accordingly as seen (and later fully computed)
	# We also introduce connections, so that we can build a small 
	# graph of where the robot knows it can go. 

	# we need better map building. if we can only see so far, 
	# That means that on the other side of the wall, there is
	# either nothing (it's the edge of the maze) or another tile. 
	# In which case, we know something about that tile. 
	def update_maze_map(self, normalized_sensors):
		
		# current space
		x = self.location[0]
		y = self.location[1]

		# seen north
		if(normalized_sensors[0] != None):
			i = 0
			while(i < normalized_sensors[0]):
				current = self.maze_graph.get_tile_ref(x, y + i)
				next_tile = self.maze_graph.get_tile_ref(x, y + i + 1)
				# link them together
				current.add_transition("N", next_tile)
				next_tile.add_transition("S", current)
				next_tile.set_connected()
				i = i + 1

			self.join_by_wall((x, y + i), (x, y+ i + 1), "N")
			
		# seen east
		if(normalized_sensors[1] != None):
			i = 0
			while(i < normalized_sensors[1]):
				current = self.maze_graph.get_tile_ref(x + i, y)
				next_tile = self.maze_graph.get_tile_ref(x + i + 1, y)
				# link them together
				current.add_transition("E", next_tile)
				next_tile.add_transition("W", current)
				next_tile.set_connected()
				i = i + 1

			self.join_by_wall((x+i, y), (x+i+1, y), "E")


		# seen south
		if(normalized_sensors[2] != None):
			i = 0
			while(i < normalized_sensors[2]):
				current = self.maze_graph.get_tile_ref(x, y-i)
				next_tile = self.maze_graph.get_tile_ref(x, y - i - 1)
				# link them together
				current.add_transition("S", next_tile)
				next_tile.add_transition("N", current)
				next_tile.set_connected()
				i = i + 1

			self.join_by_wall((x, y-i), (x, y-i-1), "S")

		# seen west
		if(normalized_sensors[3] != None):
			i = 0
			while(i < normalized_sensors[3]):
				current = self.maze_graph.get_tile_ref(x - i, y)
				next_tile = self.maze_graph.get_tile_ref(x - i - 1, y)
				# link them together
				current.add_transition("W", next_tile)
				next_tile.add_transition("E", current)
				next_tile.set_connected()
				i = i + 1

			self.join_by_wall((x-i, y), (x-i-1, y), "W")

	# destination is an (x, y) tuple. 
	def find_route(self, destination):
		# We have a graph. 
		# Our root is our current location. 
		# begin a breadth-first search for the node. 
		# we'll come across nodes already "examined", don't re-examine. 
		# lets finish implementing this later... 
		# and instead focus on an algo that finds the tile we want to explore. 
		pass

	# destination is a tile ref. 
	def calc_immediate_action(self, destination):
		# determine our current heading

		# determine which way we move from the current location 
		# to get to the destination (N, E, S, W)

		# get the tuple which is a tuple - rotation and int for move. 
	
		# key: (current_heading, direction to move)
		# value: (rotation, steps)
		action_dict = {
			("up", "N"): (0, 1),
			("up", "E"): (90, 1),
			("up", "S"): (90, 0),
			("up", "W"): (-90, 1), 

			("right", "N"): (-90, 1),
			("right", "E"): (0, 1),
			("right", "S"): (90, 1),
			("right", "W"):	(90, 0),

			("down", "N"): (90, 0),
			("down", "E"): (-90, 1),
			("down", "S"): (0, 1),
			("down", "W"): (90, 1),

			("left", "N"): (90, 1),
			("left", "E"): (90, 0), 
			("left", "S"): (-90, 1), 
			("left", "W"): (0, 1)
		}

		# determine if we need to go N, E, S, W
		current = self.maze_graph.get_tile_ref(self.location[0], self.location[1])
		direction = None
		if(current.transition.get("N") == destination):
			direction = "N"
		elif(current.transition.get("E") == destination):
			direction = "E"
		elif(current.transition.get("S") == destination):
			direction = "S"
		elif(current.transition.get("W") == destination):
			direction = "W"
		else:
			print("ERRROR ERROR ERROR - two tiles not connected!!")

		return action_dict[(self.heading, direction)]


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

		Now that we've got this done, we're going to actually start making
		decicions since we have everything we need - 
		how close is a tile to the center, and how much do we know about it. 

		hereafter, we'll refer to the distance fo the tile from the center
		as just its distance. 

		Lets try one algorithm. 
			Look at graph, and find the tile that has the smallest
			distance. If we already know everything about that tile, 
			then look for the next smallest distance. Once we find the
			smallest distance tile that isn't fully explored, plan a 
			route to get there. 

			We can make route planning robust by either trying to 
			skip tiles (covering a few in one turn if we already 
			fully explored them) or by stopping at tiles that are
			not fully explored to see if we can now get to a tile
			that is more useful to explore than the one we're going
			to right now. I think this approach *must* eventually 
			find a way to the middle.  

			The current issue is route planning. We need to know 
			how to efficiently get between two places. 
		"""	
		pass

	
	
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
		print("================================================================")
		print("Normalized sensor data: " + str(normalized_sensor_data))
		print("Current position: " + str(self.location))
		print("Current heading: " + self.heading)
		print("Move number: " + str(self.num_moves))
		completion_score = self.maze_graph.get_completion_index()
		print("completion score: " + str(completion_score) + "%")

		# Delete this later, it's for running metrics on the robot's performance
# IMORTANT FOR DEBUGING THINGY
		self.file.write(str(completion_score) + "\n")


		self.update_maze_map(normalized_sensor_data)

		# we don't need to really print the maze at this point, I think 
# THIS IS WHERE YOU CAN TOGGLE MAZE VIEW
		self.maze_graph.print_maze_view(self.location)

		# Now that we have all the data from sensors, we can 
		# determine the next waypoints - then decide which one to go to. 
		waypoints = self.maze_graph.get_next_waypoint()
		
		curr_tile = self.maze_graph.get_tile_ref(self.location[0], self.location[1])
		directions_1 = self.maze_graph.get_directions_to_waypoint(curr_tile, waypoints[0])
		directions_2 = self.maze_graph.get_directions_to_waypoint(curr_tile, waypoints[1])

		directions = None
		waypoint = None
		if(len(directions_2) + 6 < len(directions_1)):
			directions = directions_2
			waypoint = waypoints[1]
			
		else:
			directions = directions_1
			waypoint = waypoints[0]

		
		print("Waypoint: " + str(waypoint.x_coord) + ", " +  str(waypoint.y_coord))

		print("Directions:")
		num_steps = len(directions)
		i = num_steps - 1
		num_printed = 0
		while(i >= 0 and num_printed < 5):
			print(directions[i].tuple())
			i = i - 1
			num_printed = num_printed + 1

		if(num_printed < num_steps):
			print("... (" + str(num_steps - num_printed) + " more in current path)")

		immediate_action = self.calc_immediate_action(directions[num_steps - 1])
		print("Proposed action: " + str(immediate_action))

		# This is just here so that I can see everytime the state of the 
		# robot before it does something

		raw_input("Waiting to proceed...")
		unused_variable_01 = os.system('clear')

		# We'll comment out everything here with a triple quote
		#embed()	
		"""
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
		"""
		
		rotation = immediate_action[0]
		movement = immediate_action[1]

		# we can update those values, since we're currently assuming 
		self.heading = self.update_heading(self.heading, rotation)
		self.location = self.update_location(self.location, self.heading, movement)
		self.num_moves = self.num_moves + 1

		return rotation, movement
