import random
random.seed(0)
# current issues - 

"""
1) Center isn't well defined - may have too many open sides. 
2) robot may become enclosed. 
"""

"""

First generate the horizontal and vertical walls
in two different 2d arrays. 

in a 12x12 maze, there are 12 rows, and 12 columns. 

However... there are really only the internal walls we need
to care about... 
"""

""" 3x3 maze...""" 

"""
 _ _ _
|_|_|_|
|_|_|_|
|_|_|_|

"""

"""
Now we remove the walls that are mandatory... 

   
_|_|_
_|_|_
 | | 

# and we're left with 2 cols and 3 rows for vert walls, 
and 2 rows and 3 cols for horiz walls... 

and we can extend it, for the 3x3, there will be 
3 cols and 4 rows for vert walls
3 rows and 4 cols for horiz walls

which means for a 12x12 there will be
12 cols and 13 rows for vert walls
12 rows and 13 cls for horiz walls
"""


# The probability of there being a wall at a 
# particular location. 
wall_probability = 0.3

def wall_gen():
	val = random.random()
	if(val < wall_probability):
		return 1
	else:
		return 0


# I don't even care anymore, tuples is fine as keys
vert_walls = {}
for x in xrange(13):
	for y in xrange(12):
		vert_walls[(x, y)] = wall_gen()

horiz_walls = {}
for x in xrange(12):
	for y in xrange(13):
		horiz_walls[(x, y)] = wall_gen()

# now that all the walls are in place, we need
# to put in definitive walls - the edges themselves. 

# set all the walls on the sides of the maze
for y in xrange(12):
	vert_walls[(0, y)] = 1
	vert_walls[(12, y)] = 1

# set the wall to the right of the robot
# on the start tile to 1, as per specs. 
vert_walls[(1, 0)] = 1

# goal room walls shouldn't exist... 
horiz_walls[(5,6)] = 0
horiz_walls[(6,6)] = 0

vert_walls[(6, 5)] = 0
vert_walls[(6,6)] = 0

# set all the walls on the top and bottom
for x in xrange(12):
	horiz_walls[(x, 0)] = 1
	horiz_walls[(x, 12)] = 1


# Need to convert this into the tile values
tile_vals = {}
for x in xrange(12):
	for y in xrange(12):

		# north horiz
		nh = 1 - horiz_walls[(x, y + 1)]

		# south horiz
		sh = 1 - horiz_walls[(x, y)]

		# east vert
		ev = 1 - vert_walls[(x + 1, y)]

		# west vert
		wv = 1 - vert_walls[(x, y)]	

		val = nh+(ev*2)+(sh*4)+(wv*8)

		tile_vals[(x, y)] = val

# now that the tile vals are made, we can save
# them to a file. 

# we just need to print them a certain way... 
maze_output = open("maze_gen_output_01.txt", "w")
maze_output.write("12\n")

for i in xrange(12):
	for j in xrange(12):
		maze_output.write(str(tile_vals[(i, j)]))
		if(j != 11):
			maze_output.write(",")

	maze_output.write("\n")

maze_output.close()
# And we're done... I think
