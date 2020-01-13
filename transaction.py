from collections import OrderedDict


class Transaction:

	def __init__(self, sender, recipient, amount):
		self.sender = sender
		self.recipient = recipient
		self.amount = amount


	# def __str__(self):
	# 	# return str(self.__dict__)
	# 	# Custom stringification to get a consistant hash
	# 	return f'{{"sender":"{self.sender}","recipient":"{self.recipient}","amount":"{self.amount}"}}'


	def __repr__(self):
		# Custom stringification to get a consistant hash
		return f'{{"sender":"{self.sender}","recipient":"{self.recipient}","amount":"{self.amount}"}}'


	def to_ordered_dict(self):
		"""Returns an OrderedDict representation of the current Transaction object (to get a consistant hash)"""
		return OrderedDict([('sender', self.sender), ('receipient', self.recipient), ('amount', self.amount)])
