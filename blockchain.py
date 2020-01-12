from functools import reduce
import hashlib
import json
from collections import OrderedDict

# Configure Reward received for a successful mining of a block
MINING_REWARD = 10

# Configure Proof-Of-Work Difficulty: Number of leading zeros required in the hash
POW_LEADING_ZEROS = 2

# Initializing blockchain list with Genesis (first) block
GENESIS_BLOCK = {
	'previous_hash': '',		# Not required as it is the Genesis (first) block
	'index': 0,
	'transactions': [],
	'proof': 0					# Dummy proof (not required)
}
blockchain = [GENESIS_BLOCK]

# List of new transactions that are waiting to be processed (mined), i.e, included into the blockchain
open_transactions = []

# Current user
owner = 'Abhi'

# Set of all participants
participants = {'Abhi'}



def hash_block(block):
	"""Returns the SHA256 hash of the block as a string

	Arguments:
		:block: The block to hash
	"""
	# Convert string to UTF8 with encode()
	# Return string representation of SHA256 with hexdigest()
	# The "sort_keys=True" ensures that order of data remains same during multiple hashing of same block
	return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def valid_proof(transaction, last_hash, proof):
	"""Returns True, if the proof (nonce) is valid a proof-of-work,
	i.e., if it satisfies the proof-of-work condition of generating
	a hash with the pre-defined number of zeros.

	Arguments:
		:transaction: List of transactions in the block
		:last_hash: Hash of last block stored in the current block
		:proof: The Nounce number that is to be checked
	"""
	guess = (str(transaction) + str(last_hash) + str(proof)).encode()	# Combine and UTF8 encode
	guess_hash = hashlib.sha256(guess).hexdigest()
	print("GUESS HASH: ", guess_hash)
	return guess_hash[:POW_LEADING_ZEROS] == ('0' * POW_LEADING_ZEROS)


def proof_of_work():
	"""Generate and return a proof-of-work (nounce) for the given block

	Arguments:
		:block: The block for which proof-of-work is to be generated
	"""
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof = 0
	while not valid_proof(open_transactions, last_hash, proof):
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
		# reward_transaction = {
		# 	'sender': 'MINING',
		# 	'recipient': owner,
		# 	'amount': MINING_REWARD
		# }
		# OrderedDict ensures that the order of data remains same
		# so that the same hash is generated each time.
		reward_transaction = OrderedDict(
			[('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
		copied_open_transactions = open_transactions[:]
		copied_open_transactions.append(reward_transaction)
		# Mine the new block:
		last_block = blockchain[-1]				# Get the last block to generate hash
		hashed_block = hash_block(last_block)	# Get hash of the last block
		proof = proof_of_work()		# Generate proof of work
		block = {								# Create the new block
			'previous_hash': hashed_block,
			'index': len(blockchain),
			'transactions': copied_open_transactions,
			'proof': proof
		}
		# Add the new block to the blockchain
		blockchain.append(block)
		# Clear open-transactions. BUG: TODO: New transactions may have been added by now
		open_transactions = []
		print(f"Mining done. Proof = {proof}")


def verify_chain():
	"""Verifies the current blockchain and returns True if it is valid, False otherwise"""
	for (index,block) in enumerate(blockchain):
		if index == 0:
			# Ignore the Genesis block.
			continue
		if block['previous_hash'] != hash_block(blockchain[index-1]):
			# Fail verification, if the previous-hash stored in the block does not match
			# the actual hash of the previous block.
			print(f"ERROR: The previous-hash in block {index} does not match the actual hash")
			return False
		if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
			# Fail verification, if the proof-of-work is invalid,
			# i.e, it does not generate the required hash from the stored proof.
			# Ignore the last transaction in the transactions array, which is the mining reward
			print(f"ERROR: The proof-of-work in block {index} is invalid")
			return False
	# Verify the blockchain, if it did not fail anywhere in the previous loop
	return True


def get_balance(participant):
	"""Calculate and return the balance for a participant.
	It also considers the sent coins in the pending open-transactions
	to avoid double speding.

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
	"""Returns True if the Sender of the transaction has sufficient balance for the transaction

	Arguments:
		:transaction: The transaction to verify
	"""
	sender_balance = get_balance(transaction['sender'])
	return sender_balance >= transaction['amount']


def verify_all_open_transactions():
	"""Verifies all open-transactions and returns True if all are valid, False otherwise"""
	return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(amount, recipient, sender=owner):
	"""Adds the transaction to the blockchain's open-transactions queue
	if verified for sufficient balance.
	Returns True if the transaction was added successfully, False otherwise.

	Arguments:
		:sender: The sender of the coins
		:recipient: The recipient of the coins
		:amount: The amount of coins sent with the transaction
	"""
	# transaction = {
	# 	'sender': sender,
	# 	'recipient': recipient,
	# 	'amount': amount
	# }
	# OrderedDict ensures that the order of data remains same
	# so that the same hash is generated each time.
	transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
	if verify_transaction(transaction):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient)
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
