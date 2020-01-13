from time import time

class Block:

	def __init__(self, index, previous_hash, transactions, proof, timestamp=None):
		self.index = index
		self.previous_hash = previous_hash
		self.transactions = transactions
		self.proof = proof
		self.timestamp = time() if timestamp is None else timestamp


	def __repr__(self):
		# return str(self.__dict__)
		return '{{"index":{},"previous_hash":"{}","proof":{},"timestamp":{},"transactions":{}}}'.format(
			self.index,
			self.previous_hash,
			self.proof,
			self.timestamp,
			self.transactions
			# str([str(tx) for tx in self.transactions])
		)

