from math import sqrt
from heapq import heappush, heappop

def find_path(source, destination, mesh):
	dist = {}
	prev = {}
	queue = []
	path = []
	detail_points = {}
	sourceBox = None
	alt = 0

	sourceBox = find_source_box(source, mesh)
	dist[sourceBox] = 0

	destBox = find_source_box(destination, mesh)

	if sourceBox == destBox:
		return ([(source, destination)], [(sourceBox)])

	queue = [(dist[sourceBox],sourceBox,source)]
	prev[sourceBox] = None
	
	try:
		while queue:
			currentBox = heappop(queue)

			if in_box(destination, currentBox): 
				destBox = currentBox[1]
				break
			
			for next_box in mesh['adj'][currentBox[1]]:
				alt = dist[currentBox[1]] + coor_distance((currentBox[2][0],currentBox[2][1]), find_detail_points((currentBox[2][0],currentBox[2][1]), next_box))
				
				if next_box not in prev or alt < dist[next_box]:
					dist[next_box] = alt
					priority = alt  + heuristic(destination, find_detail_points((currentBox[2][0],currentBox[2][1]), next_box))
					prev[next_box] = currentBox[1]
					heappush(queue,(priority, next_box, find_detail_points((currentBox[2][0],currentBox[2][1]), next_box)))
	except:
			print "Not a valid starting point."
			return ([], [])

	if in_box(destination, currentBox):
		currentBox = currentBox[1]
		while currentBox != sourceBox:
			path.append(currentBox)
			currentBox = prev[currentBox]
		path.reverse()
		for box in path:
			detail_points[box] = (source,find_detail_points(source, box))
			if box != destBox:

				source = (find_detail_points(source, box))
		detail_points[destBox] = (source, destination)
		return detail_points.values(), prev.keys()
	else:
		print "No path possible!"
		return ([], [])

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def find_detail_points(current_coords, end_box):

    x, y = current_coords


    e_x1 = end_box[0]
    e_x2 = end_box[1]
    e_y1 = end_box[2]
    e_y2 = end_box[3]

    new_x = min(e_x2 - 1, max(e_x1, x))
    new_y = min(e_y2 - 1, max(e_y1, y))

    return(new_x, new_y)


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

def in_box(a, b):
	if a[0] >= b[1][0] and a[0] <= b[1][1] and a[1] >= b[1][2] and a[1] <= b[1][3]:
		return True
	else:
		return False

def coor_distance(a, b):
    x1 = a[0]
    x2 = b[0]

    y1 = a[1]
    y2 = b[1]

    return sqrt((x1-x2)**2+(y1-y2)**2)
