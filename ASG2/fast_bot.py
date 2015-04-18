from math import *
import time
import random

ROLLOUTS = 5

class Node:
	def __init__(self, move = None, parent = None, state = None):
		self.move = move
		self.parentNode = parent
		self.childNodes = []
		self.wins = 0
		self.visits = 0
		self.untriedMoves = state.get_moves()
		self.playerJustMoved = state.get_whos_turn()

	def UCTSelectChild(self):
		s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
		return s

	def AddChild(self, m, s):
		n = Node(move = m, parent = self, state = s)
		self.untriedMoves.remove(m)
		self.childNodes.append(n)
		return n

	def Update(self, result):
		self.visits += 1
		self.wins += result

	def __repr__(self):
		return "[M:" + str(self.move) + "W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

	def TreeToString(self, indent):
		s = self.IndentString(indent) + str(self)
		for c in self.childNodes:
			s += c.TreeToString(indent + 1)
		return s

	def IndentString(self, indent):
		s = "\n"
		for i in range(1, indent+1):
			s += "| "
		return s

	def ChildrenToString(self):
		s = ""
		for c in self.childNodes:
			s += str(c) + "\n"
		return s

def think(state, quip):

	rootnode = Node(state = state)
	begin = time.time()
	end = time.time()
	count = 0
	while True:
		node = rootnode
		state = state.copy()

		#select
		while node.untriedMoves == [] and node.childNodes != []:
			node = node.UCTSelectChild()
			state.apply_move(node.move)

		#expand
		if node.untriedMoves != []:
			m = random.choice(node.untriedMoves)
			state.apply_move(m)
			node = node.AddChild(m, state)

		#Rollout
		for i in range(ROLLOUTS):
			if state.is_terminal():
				break
			state.apply_move(random.choice(state.get_moves()))
			
		count += 1	
		#back-propagate
		while node != None:
			total_score = 0.0
			if(state.get_whos_turn() == 'red'):
				total_score = state.get_score()['red'] - state.get_score()['blue']
			else:
				total_score = state.get_score()['blue'] - state.get_score()['red']
				
			node.Update(total_score)
			node = node.parentNode

		end = time.time()
		if(end - begin >= 1):
			break

	
	print("fast_bot rollouts: "+str(count))
	count = 0
	return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move