from collections import namedtuple
from heapq import heappush, heappop
import json
from timeit import default_timer

with open('Crafting.json') as f:
	Crafting = json.load(f)

def search(graph, initial, is_goal, limit, heuristic):
	queue = []
	came_from = {} # prev
	cost_so_far = {} # dist
	total_time = {}
	name_of_neighbor = {}
	came_from[initial] = None
	cost_so_far[initial] = 0
	heappush(queue, (0, initial))
	name_of_neighbor[initial] = None
	total_time[initial] = None
	start = default_timer()

	while queue:
		pri, current = heappop(queue)
		neighbors = graph(current)

		if is_goal(current):
			#print "found"
			break
		if cost_so_far[current] > limit:
			#print "not found"
			break
		for next in neighbors:
			name, effect, cost = next
			new_cost = cost_so_far[current] + cost 
			if effect not in cost_so_far or (cost_so_far[current] + cost) < cost_so_far[effect]:
				cost_so_far[effect] = new_cost
				heappush(queue, (new_cost+ heuristic(current, next), effect))
				came_from[effect] = current
				name_of_neighbor[effect] = name
				total_time[effect] = cost

	end = default_timer()
	if is_goal(current):
		total_cost = cost_so_far[current]
		plan = []
		while name_of_neighbor[current]:
			plan.append((name_of_neighbor[current], total_time[current]))
			current = came_from[current]
		plan.reverse()
	else:
		return -1, []

	return total_cost, plan, (end - start)

def inventory_to_tuple(d):
	return tuple(d.get(name,0) for i,name in enumerate(Items))

def make_initial_state(inventory):
	return inventory_to_tuple(inventory)

def make_goal_checker(goal):
	goal_lists = []
	final_state = inventory_to_tuple(goal)
	for i, name in enumerate(Items):
		if name in goal:
			goal_lists.append(i)
	def is_goal(state):
		for i in goal_lists:
			if state[i] < final_state[i]:
				return False
		return True

	return is_goal

def make_checker(rule):
	con = ()
	req = ()
	if 'Consumes' in rule:
		con = inventory_to_tuple(rule['Consumes'])	
	if 'Requires' in rule:
		req = tuple(rule['Requires'].get(name, 0) for i, name in enumerate(Items))
	def check(state):
		if req != () and state[req.index(True)] == False:
			return False
		if con != ():
			length = len(state)
			for i in range(length):
				if state[i] < con[i]:
					return False
		return True
	return check

def make_effector(rule):
	pro = ()
	con = ()
	if 'Produces' in rule:
		pro = inventory_to_tuple(rule["Produces"])
	if 'Consumes' in rule:
		con = inventory_to_tuple(rule["Consumes"])
	def effect(state):
		new_state = []
		length = len(state)
		for i in range(length):
			value = state[i]
			if con != ():
				value -= con[i]
			value += pro[i]
			new_state.append(value)
		return tuple(new_state)

	return effect

def graph(state):
	for r in all_recipes:
		if r.check(state):
			yield(r.name, r.effect(state), r.cost)

def heuristic(current, next):
	name, effect, cost = next
	length = len(effect)
	#set priority high if higher than max_inventory
	for i in range(length):
		if effect[i] > max_inventory[i]:
			return float("inf")
	return 0

Items = Crafting['Items']

start_state = make_initial_state(Crafting['Initial'])
final_goal = make_goal_checker(Crafting['Goal'])
elapsed_time = 0.0
Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
	checker = make_checker(rule)
	effector = make_effector(rule)
	recipe = Recipe(name, checker, effector, rule['Time'])
	all_recipes.append(recipe)

limit = 500
max_inventory = (1,1,1,8,1,6,1,1,1,7,32,6,1,1,1,1,1)
total_cost, plan, elapsed_time = search(graph, start_state, final_goal, limit, heuristic)
next_state = ()

for i in plan:
	print i[0] + " " + str(i[1]) 

print "Cost: " + str(total_cost) + " Len: " + str(len(plan))
print "Elapsed time: %02d seconds" %(elapsed_time)