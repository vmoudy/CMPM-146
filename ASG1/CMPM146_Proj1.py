from p1_support import load_level, show_level
from math import sqrt
from heapq import heappush, heappop


def dijkstra(src, dst, graph, adj):
	
	came_from = {}
	cost_so_far = {}
	came_from[src] = None
	cost_so_far[src] = 0
	queue = []
	heappush(queue, (cost_so_far[src],src))

	while queue:
		node = heappop(queue)
		d, n = node

		if n == dst:
			break

		neighbors = adj(graph, n)
		for next_node in neighbors:
			d2, n2 = next_node
			new_cost = cost_so_far[n] + d2
			if n2 not in cost_so_far or new_cost < cost_so_far[n2]:
				cost_so_far[n2] = new_cost
				came_from[n2] = n
				heappush(queue, (cost_so_far[n2], n2))

	if n == dst:
		path = []
		while n:
			path.append(n)
			n = came_from[n]
		path.reverse()
		return path
	else:
		return []

def get_steps(level, cell):
	
	steps = []
	x, y = cell
	for dx in [-1,0,1]:
		for dy in [-1,0,1]:
			next_cell = (x + dx, y + dy)
			dist = sqrt(dx*dx+dy*dy)
			if dist > 0 and next_cell in level['spaces']:
				heappush(steps, (dist, next_cell))
	return steps


def test_route(filename, src_waypoint, dst_waypoint, keyFound):

	level = load_level(filename, keyFound)
	print("source = " + src_waypoint + ",", "destination = " + dst_waypoint + ",", "Key found =", keyFound, "\n")
	src = level['waypoints'][src_waypoint]
	dst = level['waypoints'][dst_waypoint]


	path = dijkstra(src, dst, level, get_steps)

	if path:
		show_level(level, path)
	else:
		show_level(level, path)
		print("No path possible!!!")

if __name__ ==  '__main__':
	test_route('level2.txt', "f", "e", True)