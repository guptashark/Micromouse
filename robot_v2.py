
class Robot_v2(object):

	def __init__(self, maze_dim):

		self.location = [0, 0]
		self.heading = 'up'
		self.maze_dim = maze_dim

	def next_move(self, sensors):
		
		rotation = 0
		movement = 0
		return rotation, movement

