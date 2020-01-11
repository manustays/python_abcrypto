from functools import reduce

#Reward received for a successful mining of a block
MINING_REWARD = 10

# Initializing blockchain list
GENESIS_BLOCK = {
	'previous_hash': '',
	'index': 0,
	'transactions': []
}
blockchain = [GENESIS_BLOCK]

# List of new transactions that are waiting to be processed (mined), i.e, included into the blockchain
open_transactions = []

# Current user
owner = 'Abhi'

# Set of all participants
participants = {'Abhi'}



# def get_last_blockchain_value():
# 	"""Returns the last value of the current blockchain"""
# 	if len(blockchain) < 1:
# 		return None
# 	else:
# 		return blockchain[-1]


def hash_block(block):
	"""Returns a hash of the block"""
	return '-'.join([str(block[key]) for key in block])	# A basic hash function


def get_balance(participant):
	"""Calculate and return the balance for a participant. It also considers the sent coins in the pending open-transactions to avoid double speding.
	Arguments:
		:participant: The person for whome to calculate the balance
	"""
	# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
	# This fetches sent amounts of transactions that were already mined (included in blockchain)
	tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
	# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
	# This fetches sent amounts of open-transactions (to avoid double spending)
	open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
	tx_sender.append(open_tx_sender)	# Add open transaction amounts for sender (sent amount)
	# Calculate total sent amount
	amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_sender, 0)

	# Fetch a list all received received coin amounts that were already mined in the blockchain
	# Here we ignore open-transactions because the receipient has not yet actually received those coins yet
	tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
	amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_recipient, 0)

	# print(f"Total Amount sent={amount_sent}, received={amount_received}")

	# Return the total balance of the person (i.e, total_received - total_spent)
	return amount_received - amount_sent


def verify_transaction(transaction):
	"""Returns True if the Sender of the transaction has sufficient balance for the transaction"""
	sender_balance = get_balance(transaction['sender'])
	return sender_balance >= transaction['amount']


def verify_all_open_transactions():
	"""Verifies all open-transactions and returns True if all are valid, False otherwise"""
	return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(amount, recipient, sender=owner):
	"""Adds the transaction to the blockchain's open-transactions queue if verified for sufficient balance.
	Returns True if the transaction was added successfully, False otherwise.

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
	if verify_transaction(transaction):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient)
		return True
	else:
		return False


def mine_block():
	"""Mine a block of the blockchain by processing and including a new transaction into the blockchain"""
	global open_transactions
	# Get the hash of last block
	if len(open_transactions) > 0:
		# Add mining reward...
		reward_transaction = {
			'sender': 'MINING',
			'recipient': owner,
			'amount': MINING_REWARD
		}
		copied_open_transactions = open_transactions[:]
		copied_open_transactions.append(reward_transaction)

		# Mine transactions...
		last_block = blockchain[-1]
		hashed_block = hash_block(last_block)
		block = {
			'previous_hash': hashed_block,
			'index': len(blockchain),
			'transactions': copied_open_transactions
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
	"""Verifies the current blockchain and returns True if it is valid, False otherwise"""
	for (index,block) in enumerate(blockchain):
		if index > 0 and block['previous_hash'] != hash_block(blockchain[index-1]):
			return False
	return True


def get_user_choice():
	"""Inputs a choice from the user"""
	print()
	print("-" * 20)
	print("Please choose")
	print("1. Add New Transaction")
	print("2. Mine Blockchain")
	print("3. View Blockchain")
	print("4. View Participants")
	print("5. View My Balance")
	print("6. Verify Open Transactions")
	print("m. Manipulate Blockchain")
	print("q. Quit")
	return input('Enter your choice: ')



take_user_input = True

while take_user_input:
	user_choice = get_user_choice()

	print()

	if user_choice == '1':
		recipient, amount = get_transaction_details()
		if add_transaction(recipient = recipient, amount = amount):
			print("Transaction Added.")
		else:
			print("Transaction Failed!")
		print("\nOpen Transactions: ", open_transactions)

	elif user_choice == '2':
		mine_block()
		print("\nBalance of {}: {:6.2f}".format(owner, get_balance(owner)))

	elif user_choice == '3':
		print_blockchain_elements()

	elif user_choice == '4':
		print(participants)

	elif user_choice == '5':
		print(get_balance(owner))

	elif user_choice == '6':
		if verify_all_open_transactions():
			print("\nAll open transactions are valid.")
		else:
			print("\nSome open transactions are invalid!")
		print("Open Transactions: ", open_transactions)

	elif user_choice == 'm':
		if len(blockchain) > 0:
			blockchain[0] = {
				'previous_hash': '',
				'index': 0,
				'transactions': [{'sender': 'Amit', 'recipient': 'Abhi', 'amount':100.0}]
			}

	elif user_choice == 'q' or user_choice == '0':
		take_user_input = False

	else:
		print('Invalid choice!')

	if not verify_chain():
		print('Invalid Blockchain!!')
		take_user_input = False


# print("Blockchain: ", blockchain)
