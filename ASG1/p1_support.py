
# Support code for P1
# https://courses.soe.ucsc.edu/courses/cmpm146/Spring15/01

def load_level(filename, keyFound):
	
	walls = {}
	spaces = {}
	waypoints = {}
	with open(filename, "r") as f:

		for j, line in enumerate(f.readlines()):
			for i, char in enumerate(line):
				if char == '\n':
					continue
				elif char.isupper():
					if char == 'L' and keyFound:
						spaces[(i, j)] = char
					else:
						walls[(i,j)] = char
				else:
					spaces[(i,j)] = char
					if char.islower():
						waypoints[char] = (i,j)


	level = { 'walls': walls,
			  'spaces': spaces,
			  'waypoints': waypoints}

	return level


def show_level(level, path=[]):
	space_cells = list(level['spaces'].keys())
	wall_cells = list(level['walls'].keys())
	xs, ys = zip(*(space_cells + wall_cells))
	x_lo = min(xs)
	x_hi = max(xs)
	y_lo = min(ys)
	y_hi = max(ys)

	path_cells = set(path)

	chars = []

	for j in range(y_lo, y_hi+1):
		for i in range(x_lo, x_hi+1):

			cell = (i,j)
			if cell in path_cells:
				chars.append('*')
			elif cell in level['walls']:
				chars.append(level['walls'][cell])
			elif cell in level['spaces']:
				chars.append(level['spaces'][cell])
			else:
				chars.append(' ')
				
		chars.append('\n')

	print (''.join(chars))
