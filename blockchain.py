from functools import reduce
# from collections import OrderedDict
# import json
import pickle

from block import Block
from transaction import Transaction
from utility.hash_util import hash_block
from utility.verification import Verification


# Configure Reward received for a successful mining of a block
MINING_REWARD = 10

# Configure Proof-Of-Work Difficulty: Number of leading zeros required in the hash
POW_LEADING_ZEROS = 2


class Blockchain:

	def __init__(self, hosting_node_id):

		# Initializing the Blockchain with the genesis (first) block
		genesis_block = Block(0,'',[],0,0)
		self.__chain = [genesis_block]
		self.hosting_node = hosting_node_id

		# List of new unhandled transactions that are waiting to be processed (mined)
		# and included into the blockchain
		self.__open_transactions = []

		self.mining_difficulty = POW_LEADING_ZEROS
		self.mining_reward = MINING_REWARD

		# Load any saved Blockchain
		self.load_data()


	def get_chain(self):
		return self.__chain[:]


	def get_open_transactions(self):
		return self.__open_transactions[:]


	def load_data(self):
		"""Loads the blockchain and the open-transactions data from file"""
		try:
			with open('blockchain_store.p', mode='rb') as f:
				file_content = pickle.loads(f.read())
				self.__chain = file_content['blockchain']
				self.__open_transactions = file_content['open_transactions']
		except (IOError, IndexError):
			print('Blockchain save file not found. Starting a new Blockchain!')


	def save_data(self):
		"""Saves the blockchain and the open-transactions data into file"""
		try:
			with open('blockchain_store.p', mode='wb') as f:
				save_data = {
					'blockchain': self.__chain,
					'open_transactions': self.__open_transactions
				}
				f.write(pickle.dumps(save_data))
		except IOError:
			print('Saving blockchain failed!')


	def get_balance(self):
		"""Calculate and return the balance of the current node.
		It also considers the sent coins in the pending open-transactions
		to avoid double speding.
		"""
		participant = self.hosting_node
		# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
		# This fetches sent amounts of transactions that were already mined (included in blockchain)
		tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
		# Fetch a list of all sent coin amounts for the given person (empty lists returned if the person was not the sender)
		# This fetches sent amounts of open-transactions (to avoid double spending)
		open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
		tx_sender.append(open_tx_sender)	# Add open transaction amounts for sender (sent amount)
		# Calculate total sent amount
		amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_sender, 0)

		# Fetch a list all received received coin amounts that were already mined in the blockchain
		# Here we ignore open-transactions because the receipient has not yet actually received those coins yet
		tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
		amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + (sum(tx_amt) if len(tx_amt) > 0 else 0), tx_recipient, 0)

		# print(f"Total Amount sent={amount_sent}, received={amount_received}")

		# Return the total balance of the person (i.e, total_received - total_spent)
		return amount_received - amount_sent


	def add_transaction(self, amount, recipient, sender):	# sender=self.owner
		"""Adds the transaction to the blockchain's open-transactions queue
		if verified for sufficient balance.
		Returns True if the transaction was added successfully, False otherwise.

		Arguments:
			:sender: The sender of the coins
			:recipient: The recipient of the coins
			:amount: The amount of coins sent with the transaction
		"""
		transaction = Transaction(sender, recipient, amount)
		if Verification.verify_transaction(transaction, self.get_balance):
			self.__open_transactions.append(transaction)
			self.save_data()
			return True
		else:
			return False


	def proof_of_work(self):
		"""Generate and return a proof-of-work (nonce) for the given block

		Arguments:
			:block: The block for which proof-of-work is to be generated
		"""
		last_block = self.__chain[-1]
		last_hash = hash_block(last_block)
		proof = 0
		while not Verification.valid_proof(self.__open_transactions, last_hash, proof, self.mining_difficulty):
			proof += 1
		return proof


	def mine_block(self):
		"""Mine a block of the blockchain by processing and including
		all pending open-transactions into the blockchain"""
		# Mine a block if there are pending transactions in the open-transactions list
		if len(self.__open_transactions) > 0:
			print ('Mining started...')
			# Add mining reward...
			# OrderedDict ensures that the order of data remains same
			# so that the same hash is generated each time.
			# reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', self.mining_reward)])
			reward_transaction = Transaction('MINING', self.hosting_node, self.mining_reward)
			copied_open_transactions = self.__open_transactions[:]
			copied_open_transactions.append(reward_transaction)
			# Mine the new block:
			last_block = self.__chain[-1]				# Get the last block to generate hash
			hashed_block = hash_block(last_block)	# Get hash of the last block
			proof = self.proof_of_work()		# Generate proof of work
			block = Block(len(self.__chain), hashed_block, copied_open_transactions, proof)	# Create the new block
			# Add the new block to the blockchain
			self.__chain.append(block)
			# Clear open-transactions. BUG: TODO: New transactions may have been added by now
			self.__open_transactions = []
			print(f"Mining done. Proof = {proof}")
			self.save_data()
