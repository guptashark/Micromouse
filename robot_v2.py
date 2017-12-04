
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

		self.location = [0, 0]
		self.heading = 'up'
		self.maze_dim = maze_dim

		# Set the algorithm that will be used. 
		self.algo = ManualControl(maze_dim)

	def next_move(self, sensors):

		# pass the graph, heading and location. 
		# Extendible. 
		info_to_algo = {
			"graph": None,
			"heading": self.heading,
			"location": self.location
		}

		rotation, movement = self.algo.next_move(**info_to_algo)
		return rotation, movement

