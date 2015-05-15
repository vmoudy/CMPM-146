from p6_game import Simulator
import Queue

ANALYSIS = {}

def analyze(design):
	sim = Simulator(design)
	init = sim.get_initial_state()
	moves = sim.get_moves()
	next_state = sim.get_next_state(init, moves[0])

	queue = Queue.Queue()
	queue.put(next_state)
	ANALYSIS[next_state] = None
	while not queue.empty():
		current = queue.get()
		for i in range(0, 4):
			next = sim.get_next_state(current, moves[i])
			if next == None:
				continue
			if next not in ANALYSIS:
				queue.put(next)
				ANALYSIS[next] = current

def inspect((i,j), draw_line):
	path = []
	for n in ANALYSIS:
		pos, abil = n
		if pos == (i, j):
			path.append(n)

	for paths in path:
		current = paths
		pos, abil = paths
		while current:
			if current == None:
				break
			elif ANALYSIS[current] == None:
				break
			else:
				p, a = current
				draw_line(p, ANALYSIS[current][0], abil, paths)
				current = ANALYSIS[current]