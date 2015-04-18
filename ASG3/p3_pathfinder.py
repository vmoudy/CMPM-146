from heapq import heappush, heappop
import random
import Queue

def find_path(source_point, destination_point, mesh):
	queue = Queue.Queue()
	prev = {}
	prev_box = {}
	visited = []
	detail_points = {}
	path = []

	print str(source_point) + str(destination_point)

	source_box = find_source_box(source_point, mesh)
	visited.append(source_box)
	dest_box = find_source_box(destination_point, mesh)
	visited.append(dest_box)

	queue.put(source_box)
	prev[source_box] = None
	prev_box[source_box] = source_box
	detail_points[source_box] = source_point
	detail_points[dest_box] = destination_point

	while not queue.empty():
		current_box = queue.get()		

		if current_box == dest_box:
			break

		for next in mesh['adj'][current_box]:
			if next not in prev:
				queue.put(next)
				prev[next] = current_box
				prev_box[next] = current_box
				if next != dest_box:
					detail_points[next] = find_detail_points(detail_points[current_box], next)
				visited.append(next)

	if current_box == dest_box:
		while current_box:
			path.append((detail_points[prev_box[current_box]], detail_points[current_box]))
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