import difflib

class SpellCheck:
	
	def __init__(self, words = []):
		self.words = words
	
	def match(self, word, tolerance = 0.8):
		matches = {}
		for w in self.words:
			diff = difflib.SequenceMatcher(None, word, w).ratio()
			if diff >= tolerance:
				matches[w] = diff
		return { k: matches[k] for k in sorted(matches, key=matches.get, reverse=True)}
	
	def best_match(self, word, tolerance = 0.8):
		best_diff = 0
		best_word = None
		matches = self.match(word, tolerance)
		for w in matches:
			if matches[w] >= best_diff:
				best_diff = matches[w]
				best_word = w
		return best_word
	
	def one_match(self, word, tolerance = 0.8):
		matches = self.match(word, tolerance)
		return matches.keys()[0] if len(matches) == 1 else None

