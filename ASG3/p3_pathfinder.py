from heapq import heappush, heappop
import random
import Queue

def find_path(source_point, destination_point, mesh):
	#BFS queue
	#queue = Queue.Queue()

	#A* queue
	queue = Queue.PriorityQueue()

	prev = {}
	cost_so_far = {}
	prev_box = {}
	visited = []
	detail_points = {}
	path = []

	source_box = find_source_box(source_point, mesh)
	visited.append(source_box)
	dest_box = find_source_box(destination_point, mesh)
	visited.append(dest_box)

	if source_box == dest_box:
		return ([(source_point, destination_point)], [(source_box)])

	#BFS queue
	#queue.put(source_box)

	#A* queue
	queue.put(source_box, 0)
	cost_so_far[source_box] = 0

	prev[source_box] = None
	prev_box[source_box] = source_box
	detail_points[source_box] = source_point
	detail_points[dest_box] = destination_point

	#BFS with early exit
	"""while not queue.empty():
		current_box = queue.get()		

		if current_box == dest_box:
			break
		try:
			for next in mesh['adj'][current_box]:
				if next not in prev:
					queue.put(next)
					prev[next] = current_box
					prev_box[next] = current_box
					
					detail_points[next] = find_detail_points(detail_points[current_box], next)
					visited.append(next)
		except:
			print "Not a valid starting point."
			return ([], [])
	"""


	#A*
	while not queue.empty():
		current_box = queue.get()

		if current_box == dest_box:
			break

		try:
			for next in mesh['adj'][current_box]:
				src = detail_points[current_box]
				dest = find_detail_points(src, next)
				new_cost = cost_so_far[current_box] + cost_path(src, dest)
				if next not in cost_so_far or new_cost < cost_so_far[next]:
					detail_points[next] = find_detail_points(detail_points[current_box], next)
					cost_so_far[next] = new_cost
					priority = heuristic(detail_points[next], destination_point)
					queue.put(next, priority)
					prev[next] = current_box
					prev_box[next] = current_box
					visited.append(next)
		except:
			print "Not a valid starting point."
			return([], [])


	#find path working backwards to source
	if current_box == dest_box:
		while current_box:
			path.append((detail_points[prev_box[current_box]], detail_points[current_box]))
			if prev[current_box] == None:
				path.append((detail_points[dest_box], destination_point))
			current_box = prev[current_box]
	else:
		print "No path possible!"
		return ([], [])

	return(path, visited)


def find_source_box(xy_coord, mesh):

	for box in mesh['boxes']:

		x1 = box[0]
		x2 = box[1]
		y1 = box[2]
		y2 = box[3]
		start_x, start_y = xy_coord

		if start_x < x2 and start_x > x1:
			if start_y < y2 and start_y > y1:
				return box

def find_detail_points(current_coords, end_box):

	x, y = current_coords
	
	e_x1 = end_box[0]
	e_x2 = end_box[1]
	e_y1 = end_box[2]
	e_y2 = end_box[3]

	new_x = min(e_x2 - 1, max(e_x1, x))
	new_y = min(e_y2 - 1, max(e_y1, y))

	return(new_x, new_y)

def heuristic(src, dest):
	x,y = src
	x1, y1 = dest
	#print abs(x - x1) + abs(y - y1)
	return abs(x - x1) + abs(y - y1)

def cost_path(src, dest):
	x, y = src
	x2, y2 = dest
	return sqrt(x*x2 + y*y2)
