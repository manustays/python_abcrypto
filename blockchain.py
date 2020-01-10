# Initializing blockchain list
genesis_block = {
	'previous_block': '',
	'index': 0,
	'transactions': []
}
blockchain = [genesis_block]

# List of new transactions that are waiting to be processed (mined), i.e, included into the blockchain
open_transactions = []

# Current user
owner = 'Abhi'


# def get_last_blockchain_value():
# 	"""Returns the last value of the current blockchain"""
# 	if len(blockchain) < 1:
# 		return None
# 	else:
# 		return blockchain[-1]


def add_transaction(amount, recipient, sender=owner):
	"""Appends a new value as well as the last blockchain value to the blockchain

	Arguments:
		:sender: The sender of the coins
		:recipient: The recipient of the coins
		:amount: The amount of coins sent with the transaction
	"""
	transaction = {
		'sender': sender,
		'recipient': recipient,
		'amount': amount
	}
	open_transactions.append(transaction)


def mine_block():
	"""Mine a block of the blockchain by processing and including a new transaction into the blockchain"""
	global open_transactions
	# Get the hash of last block
	if len(open_transactions) > 0:
		last_block = blockchain[-1]
		hashed_block = '-'.join([str(last_block[key]) for key in last_block])	# A basic hash function
		block = {
			'previous_block': hashed_block,
			'index': len(blockchain),
			'transactions': open_transactions
		}
		blockchain.append(block)
		open_transactions = []


def get_transaction_details():
	"""Inputs the transaction details (recipient & amount) from the user and returns it"""
	tx_recipient = input('Enter the recipient of the transaction: ')
	tx_amount =  float(input('Enter the transaction amount: '))
	return (tx_recipient, tx_amount)


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


def get_user_choice():
	"""Inputs a choice from the user"""
	print()
	print("-" * 20)
	print("Please choose")
	print("1. Add New Transaction")
	print("2. Mine Blockchain")
	print("3. View Blockchain")
	print("m. Manipulate Blockchain")
	print("q. Quit")
	return input('Enter your choice: ')



take_user_input = True

while take_user_input:
	user_choice = get_user_choice()

	print()

	if user_choice == '1':
		recipient, amount = get_transaction_details()
		add_transaction(recipient = recipient, amount = amount)
		print("\nOpen Transactions: ", open_transactions)

	elif user_choice == '2':
		mine_block()

	elif user_choice == '3':
		print_blockchain_elements()

	elif user_choice == 'm':
		if len(blockchain) > 0:
			blockchain[0] = [2]

	elif user_choice == 'q' or user_choice == '0':
		take_user_input = False

	else:
		print('Invalid choice!')

	# if not verify_chain():
	# 	print('Invalid Blockchain!!')
	# 	take_user_input = False


# print("Blockchain: ", blockchain)
