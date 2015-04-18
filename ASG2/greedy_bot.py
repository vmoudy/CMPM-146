import random
ROLLOUTS = 1

def think(state, quip):
	moves = state.get_moves()

	best_move = moves[0]
	best_score = float('-inf')

	me = state.get_whos_turn()

	def outcome(score):
		if me == 'red':
			return score['red'] - score['blue']
		else:
			return score['blue'] - score['red']

	for move in moves:
		score = 0.0

		rollout_state = state.copy()
		rollout_state.apply_move(move)

		for i in range(ROLLOUTS):
			if rollout_state.is_terminal():
				break
			rollout_state.apply_move(random.choice(rollout_state.get_moves()))

		score = outcome(rollout_state.get_score())
		
		if score > best_score:
			best_score = score
			best_move = move

	return best_move
