from string import zfill

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
				current_str = current_str + str(current.get_num_known_adjacents()).zfill(2) + " "
			print current_str
			current_str = ""

		
