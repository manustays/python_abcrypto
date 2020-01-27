from collections import OrderedDict


class Transaction:

	def __init__(self, sender, recipient, amount, signature):
		self.sender = sender
		self.recipient = recipient
		self.amount = amount
		self.signature = signature


	# def __str__(self):
	# 	# return str(self.__dict__)
	# 	# Custom stringification to get a consistant hash
	# 	return f'{{"sender":"{self.sender}","recipient":"{self.recipient}","amount":"{self.amount}"}}'


	def __repr__(self):
		# Custom stringification to get a consistant hash
		return f'{{"sender":"{self.sender}","recipient":"{self.recipient}","amount":"{self.amount}","signature":"{self.signature}"}}'


	@classmethod
	def from_dict(cls, transaction):
		"""Factory function to return a Transaction object from a dictionary of transaction data

		Arguments:
			:transaction: A transaction dictionary to convert into object
		"""
		return cls(transaction.sender, transaction.recipient, transaction.amount, transaction.signature)


	def to_dict(self):
		"""Get a copy of the transaction as a dict"""
		return self.__dict__.copy()


	def to_ordered_dict(self):
		"""Returns an OrderedDict representation of the current Transaction object (to get a consistant hash)"""
		return OrderedDict([('sender', self.sender), ('receipient', self.recipient), ('amount', self.amount), ('signature',self.signature)])
