# Initializing blockchain list
blockchain = []	# [[1]]


def get_last_blockchain_value():
	"""Returns the last value of the current blockchain"""
	if len(blockchain) < 1:
		return None
	else:
		return blockchain[-1]


def add_transaction(transaction_amount):
	"""Appends a new value as well as the last blockchain value to the blockchain

	Arguments:
		:transaction_amount: The amount to add to the blockchain
	"""
	last_blockchain_value = get_last_blockchain_value()
	if last_blockchain_value == None:
		blockchain.append([transaction_amount])
	else:
		blockchain.append([last_blockchain_value, transaction_amount])
	# print(blockchain)


def get_transaction_amount():
	"""Inputs a transaction amount from the user and returns it as float"""
	return float(input('Enter the transaction amount: '))


def get_user_choice():
	"""Inputs a choice from the user"""
	print("\nPlease choose")
	print("1. Add a new transaction value")
	print("2. View blockchain")
	print("m. Manipulate blockchain")
	print("q. Quit")
	return input('Enter your choice: ')


def print_blockchain_elements():
	"""Print all the blocks of the blockchain"""
	for block in blockchain:
		print("Block: ", block)


def verify_chain():
	"""Verifies the integrity of the blockchain"""
	is_valid = True
	block_index = 0
	for block in blockchain:
		if block_index > 0 and block[0] != blockchain[block_index-1]:
			is_valid = False
		block_index += 1
	return is_valid



take_user_input = True

while take_user_input:
	user_choice = get_user_choice()

	if user_choice == '1':
		add_transaction(get_transaction_amount())

	elif user_choice == '2':
		print_blockchain_elements()

	elif user_choice == 'm':
		if len(blockchain) > 0:
			blockchain[0] = [2]

	elif user_choice == 'q' or user_choice == '0':
		take_user_input = False

	else:
		print('Invalid choice!')

	if not verify_chain():
		print('Invalid Blockchain!!')
		take_user_input = False


# print("Blockchain: ", blockchain)
