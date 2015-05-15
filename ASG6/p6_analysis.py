from p6_game import Simulator
import Queue

ANALYSIS = {}

def analyze(design):
	sim = Simulator(design)
	init = sim.get_initial_state()
	moves = sim.get_moves()
	next_state = sim.get_next_state(init, moves[0])
	position, ability = next_state
	i, j = position

	queue = Queue.Queue()
	queue.put(next_state)
	ANALYSIS[position] = None
	while not queue.empty():
		current = queue.get()
		p, a = current
		for i in range(0, 4):
			next = sim.get_next_state(current, moves[i])
			if next == None:
				continue
			pos, abil = next
			if pos not in ANALYSIS:
				queue.put(next)
				ANALYSIS[pos] = p

def inspect((i,j), draw_line):
	if (i, j) in ANALYSIS:
		n = ANALYSIS[(i,j)]
		draw_line(n, (i, j))
		path = []
		while n:
			path.append(n)
			if ANALYSIS[n] != None:
				draw_line(ANALYSIS[n], n)
			n = ANALYSIS[n]
	else:
		print "No path possible."
