from functools import reduce
from collections import OrderedDict
# import json
import pickle

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification


# Configure Reward received for a successful mining of a block
MINING_REWARD = 10

# Configure Proof-Of-Work Difficulty: Number of leading zeros required in the hash
POW_LEADING_ZEROS = 2

# The Blockchain: a list of blocks of processed transactions
blockchain = []

# List of new unhandled transactions that are waiting to be processed (mined)
# and included into the blockchain
open_transactions = []

# Current user
owner = 'Abhi'

# Set of all participants
# participants = {'Abhi'}



def load_data():
	"""Loads the blockchain and the open-transactions data from file"""
	global blockchain
	global open_transactions

	try:
		with open('blockchain_store.p', mode='rb') as f:
			file_content = pickle.loads(f.read())
			blockchain = file_content['blockchain']
			open_transactions = file_content['open_transactions']

		## LOAD FROM TEXT FILE FOR EASIER DEBUGGING...
		# with open('blockchain_store.txt', mode='r') as f:
		# 	file_content = f.readlines()
		# 	blockchain = json.loads(file_content[0][:-1])	# Exclude '\n' at the end of the line
		# 	updated_blockchain = []
		# 	for block in blockchain:
		# 		updated_block = {
		# 			'previous_hash': block['previous_hash'],
		# 			'index': block['index'],
		# 			'transactions': [OrderedDict(
		# 		[('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']],
		# 			'proof': block['proof']
		# 		}
		# 		updated_blockchain.append(updated_block)
		# 	blockchain = updated_blockchain
		# 	open_transactions = json.loads(file_content[1])
		# 	updated_open_transactions = []
		# 	for tx in open_transactions:
		# 		updated_transaction = OrderedDict(
		# 		[('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
		# 		updated_open_transactions.append(updated_transaction)
		# 	open_transactions = updated_open_transactions

	except (IOError, IndexError):
		print('Blockchain save file not found!')
		# Initializing blockchain list with Genesis (first) block
		genesis_block = Block(0,'',[],0,0)
		# {
		# 	'previous_hash': '',		# Not required as it is the Genesis (first) block
		# 	'index': 0,
		# 	'transactions': [],
		# 	'proof': 0					# Dummy proof (not required)
		# }
		blockchain = [genesis_block]
		# Initialize open-transactions
		open_transactions = []


load_data()		# Load Data as soon as the program starts


def save_data():
	"""Saves the blockchain and the open-transactions data into file"""
	try:
		with open('blockchain_store.p', mode='wb') as f:
			save_data = {
				'blockchain': blockchain,
				'open_transactions': open_transactions
			}
			f.write(pickle.dumps(save_data))

		## STORE IN A TEXT FILE FOR EASIER DEBUGGING...
		# with open('blockchain_store.txt', mode='w') as f:
			# f.write(json.dumps(blockchain))
			# f.write('\n')
			# f.write(json.dumps(open_transactions))

	except IOError:
		print('Saving blockchain failed!')


def proof_of_work():
	"""Generate and return a proof-of-work (nonce) for the given block

	Arguments:
		:block: The block for which proof-of-work is to be generated
	"""
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof = 0
	verifier = Verification()
	while not verifier.valid_proof(open_transactions, last_hash, proof, POW_LEADING_ZEROS):
		proof += 1
	return proof


def mine_block():
	"""Mine a block of the blockchain by processing and including
	all pending open-transactions into the blockchain"""
	global open_transactions

	# Mine a block if there are pending transactions in the open-transactions list
	if len(open_transactions) > 0:
		print ('Mining started...')
		# Add mining reward...
		# OrderedDict ensures that the order of data remains same
		# so that the same hash is generated each time.
		# reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
		reward_transaction = Transaction('MINING', owner, MINING_REWARD)
		copied_open_transactions = open_transactions[:]
		copied_open_transactions.append(reward_transaction)
		# Mine the new block:
		last_block = blockchain[-1]				# Get the last block to generate hash
		hashed_block = hash_block(last_block)	# Get hash of the last block
		proof = proof_of_work()		# Generate proof of work
		block = Block(len(blockchain), hashed_block, copied_open_transactions, proof)	# Create the new block
		# Add the new block to the blockchain
		blockchain.append(block)
		# Clear open-transactions. BUG: TODO: New transactions may have been added by now
		open_transactions = []
		print(f"Mining done. Proof = {proof}")
		save_data()



def get_balance(participant):
	"""Calculate and return the balance for a participant.
	It also considers the sent coins in the pending open-transactions
	to avoid double speding.

	Arguments:
		:participant: The person for whome to calculate the balance
	"""
	# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
	# This fetches sent amounts of transactions that were already mined (included in blockchain)
	tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
	# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
	# This fetches sent amounts of open-transactions (to avoid double spending)
	open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
	tx_sender.append(open_tx_sender)	# Add open transaction amounts for sender (sent amount)
	# Calculate total sent amount
	amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_sender, 0)

	# Fetch a list all received received coin amounts that were already mined in the blockchain
	# Here we ignore open-transactions because the receipient has not yet actually received those coins yet
	tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in blockchain]
	amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_recipient, 0)

	# print(f"Total Amount sent={amount_sent}, received={amount_received}")

	# Return the total balance of the person (i.e, total_received - total_spent)
	return amount_received - amount_sent


def add_transaction(amount, recipient, sender=owner):
	"""Adds the transaction to the blockchain's open-transactions queue
	if verified for sufficient balance.
	Returns True if the transaction was added successfully, False otherwise.

	Arguments:
		:sender: The sender of the coins
		:recipient: The recipient of the coins
		:amount: The amount of coins sent with the transaction
	"""
	# OrderedDict ensures that the order of data remains same
	# so that the same hash is generated each time.
	# transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])

	transaction = Transaction(sender,recipient,amount)
	verifier = Verification()
	if verifier.verify_transaction(transaction, get_balance):
		open_transactions.append(transaction)
		# participants.add(sender)
		# participants.add(recipient)
		save_data()
		return True
	else:
		return False


def get_transaction_details():
	"""Inputs the transaction details (recipient & amount) from the user and returns it"""
	tx_recipient = input('Enter the recipient of the transaction: ')
	tx_amount =  float(input('Enter the transaction amount: '))
	return (tx_recipient, tx_amount)


def print_blockchain_elements():
	"""Print all the blocks of the blockchain"""
	for block in blockchain:
		print("Block: ", block)


def get_user_choice():
	"""Inputs a choice from the user"""
	print()
	print("-" * 20)
	print("  SELECT AN OPTION")
	print("-" * 20)
	print("1. Add New Transaction")
	print("2. Mine Blockchain")
	print("3. View Blockchain")
	# print("4. View Participants")
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

	# elif user_choice == '4':
	# 	print(participants)

	elif user_choice == '5':
		print("\nBalance of {}: {:6.2f}".format(owner, get_balance(owner)))

	elif user_choice == '6':
		verifier = Verification()
		if verifier.verify_open_transactions(open_transactions, get_balance):
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

	verifier = Verification()
	if not verifier.verify_chain(blockchain, POW_LEADING_ZEROS):
		print('Invalid Blockchain!!')
		take_user_input = False


# print("Blockchain: ", blockchain)
