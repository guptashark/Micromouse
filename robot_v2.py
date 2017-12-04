
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
		location_output = "Location: " + str(location)
		heading_output = "Heading: " + heading
		output = location_output + "\t" + heading_output
		
		print(output)
		

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

	# Do this first, so that update_location works. 
	def update_heading(self, rotation):
		
		index_change = rotation / 90
		self.heading_index += index_change
		
		if(self.heading_index < 0):
			self.heading_index += 4
			
		if(self.heading_index > 4):
			self.heading_index += -4

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

		# Pass the data necessary to render
		# info on the maze before the algo runs. 
		# (To see what the input to the algo is)
		info_to_view = {
			"graph": None,
			"heading": self.heading,
			"location": self.location
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

