
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
		pass

	# Print before the algo runs, to see what the algo
	# is working with. 
	def pre_algo_view(self, **kwargs):
		# location and heading are basic. Always print. 
		location = kwargs["location"]
		heading = kwargs["heading"]
		normalized_sensors = kwargs["normalized_sensors"]

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

	def normalize_sensors(self, sensors):
		"""	
		N	0	slice at 1
		[W, N, E, -]
		[N, E, -, W] = [N, E, -] + [w]
		1
		

		E	1	slice at 0
		[N, E, S, -]
		[N, E, S, -] = [N, E, S, -]
		0

		S	2	slice at 3
		[E, S, W, -]
		[-, E, S, W] = [-] + [E, S, W]
		None... 

		W	3	slice at 2
		[S, W, N, -] = [N, -] + [S, W]
		[N, -, S, W]
		2
		"""

		# There could be a better way to do this... 
		# but just take the index and do the slicing. 
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

		# Pass the data necessary to render
		# info on the maze before the algo runs. 
		# (To see what the input to the algo is)

		
		info_to_view = {
			"graph": None,
			"heading": self.heading,
			"location": self.location,
			"normalized_sensors": normalized_sensors
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

