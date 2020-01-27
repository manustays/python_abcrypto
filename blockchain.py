from functools import reduce
# from collections import OrderedDict
# import json
import pickle
import requests

from block import Block
from transaction import Transaction
from utility.hash_util import hash_block
from utility.verification import Verification
from wallet import Wallet


# Configure Reward received for a successful mining of a block
MINING_REWARD = 10

# Configure Proof-Of-Work Difficulty: Number of leading zeros required in the hash
POW_LEADING_ZEROS = 3


class Blockchain:

	def __init__(self, hosting_node_id):
		# Initializing the Blockchain with the genesis (first) block
		genesis_block = Block(0,'',[],0,0)
		self.__chain = [genesis_block]
		self.__hosting_node = hosting_node_id
		self.__peer_nodes = set()
		self.resolve_conflicts = False			# Set to True, when there is a conflict to be resolved

		# List of new unhandled transactions that are waiting to be processed (mined)
		# and included into the blockchain
		self.__open_transactions = []

		self.mining_difficulty = POW_LEADING_ZEROS
		self.mining_reward = MINING_REWARD

		# Load any saved Blockchain
		self.load_data()


	def get_chain(self):
		"""Returns a copy of the current blockchain"""
		return self.__chain[:]


	def get_chain_dict(self):
		"""Returns a copy of the current blockchain as a pure dict"""
		dict_chain = [block.to_dict() for block in self.get_chain()]
		return dict_chain


	def get_length(self):
		"""Returns the length of the current blockchain"""
		return len(self.__chain)


	def get_last_block(self):
		"""Returns a copy of the last block of the current blockchain"""
		return self.__chain[:][-1]


	def get_open_transactions(self):
		"""Returns a copy of the open transactions"""
		return self.__open_transactions[:]


	def load_data(self):
		"""Loads the blockchain and the open-transactions data from file"""
		try:
			with open('blockchain_store.p', mode='rb') as f:
				file_content = pickle.loads(f.read())
				self.__chain = file_content['blockchain']
				self.__open_transactions = file_content['open_transactions']
				self.__peer_nodes = file_content['peer_nodes']
		except (IOError, IndexError):
			print('Blockchain save file not found. Starting a new Blockchain!')


	def save_data(self):
		"""Saves the blockchain and the open-transactions data into file"""
		try:
			with open('blockchain_store.p', mode='wb') as f:
				save_data = {
					'blockchain': self.__chain,
					'open_transactions': self.__open_transactions,
					'peer_nodes': self.__peer_nodes
				}
				f.write(pickle.dumps(save_data))
		except IOError:
			print('Saving blockchain failed!')


	def get_balance(self, sender=None):
		"""Calculate and return the balance of the sender node (by default, the current node).
		It also considers the sent coins in the pending open-transactions
		to avoid double speding.

		Arguments:
			:sender: The node whose balance is to be calculated
		"""
		if sender == None:
			if self.__hosting_node == None:
				return None
			participant = self.__hosting_node
		else:
			participant = sender

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


	def add_transaction(self, sender, recipient, amount, signature, is_receiving=False):
		"""Adds the transaction to the blockchain's open-transactions queue
		if verified for sufficient balance.
		Returns True if the transaction was added successfully, False otherwise.

		Arguments:
			:sender: The sender of the coins
			:recipient: The recipient of the coins
			:amount: The amount of coins sent with the transaction
			:signature: The cryptographic signature of the transaction signed by sender's private-key
			:is_receiving: Is this new transaction being received from another node as a broadcast?
		"""
		# if self.__hosting_node == None:
		# 	return False
		transaction = Transaction(sender, recipient, amount, signature)
		if Verification.verify_transaction(transaction, self.get_balance):
			self.__open_transactions.append(transaction)
			self.save_data()

			# Broadcast to all nodes...
			# BUG: THIS WILL SLOW DOWN 'add_transaction' HTTPS requests because it will wait till all broadcasting is also done and may lead to timeout
			# TODO: BROADCAST asynchronously AFTER adding transaction
			if not is_receiving:
				broadcasted = self.broadcast('broadcast-transaction', {'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature })
				if not broadcasted:
					print('Transaction declined, needs resolving')
					return False		# TODO: Resolve conflict

			return True
		else:
			# TODO: If a transaction verification fails (due to signature), remove it from open_transactions
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
		if self.__hosting_node == None:
			return None
		# Mine a block if there are pending transactions in the open-transactions list
		if len(self.__open_transactions) > 0:
			# print ('Mining started...')
			# Add mining reward...
			# OrderedDict ensures that the order of data remains same
			# so that the same hash is generated each time.
			# reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', self.mining_reward)])
			reward_transaction = Transaction('MINING', self.__hosting_node, self.mining_reward, '')
			copied_open_transactions = self.__open_transactions[:]
			# Verify open transactions
			for tx in copied_open_transactions:
				if not Wallet.verify_transaction_signature(tx):
					return None
			# Append mining reward to open transactions
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
			# print(f"Mining done. Proof = {proof}")
			self.save_data()

			# Broadcast to all nodes...
			# BUG: THIS WILL SLOW DOWN 'mine_block' HTTPS requests because it will wait till all broadcasting is also done and may lead to timeout
			# TODO: BROADCAST asynchronously AFTER mining
			# if not is_receiving:
			broadcasted = self.broadcast('broadcast-block', {'block': block.to_dict() })
			if not broadcasted:
				print('Block declined, needs resolving')
				# return None	# TODO: Resolve conflict

			return block
		else:
			return None


	def add_block(self, block):
		"""Validates and adds an already mined block that was broadcast by another node

		Arguments:
			:block: The block to add that was broadcast by another node
		"""
		transactions = [Transaction.from_dict(tx) for tx in block['transactions']]
		proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'], self.mining_difficulty)
		hashes_match = hash_block(self.__chain[-1]) == block['previous']
		if not proof_is_valid or not hashes_match:
			return False

		self.__chain.append(Block.from_dict(block))

		# Update open-transactions: remove any transaction that is already mined...
		stored_transactions = self.__open_transactions[:]
		for itx in block['transactions']:		# incoming transactions
			for otx in stored_transactions:		# open transactions
				if otx.sender == itx['sender'] and otx.recipient == itx['recipient'] and otx.amount == itx['amount'] and otx.signature == itx['signature']:
					try:
						self.__open_transactions.remove(otx)
					except ValueError:
						pass

		self.save_data()
		return True


	def resolve(self):
		"""Resolves any conflict in the current blockchain"""
		winner_chain = self.__chain
		replace = False
		for node in self.__peer_nodes:
			url = 'http://{}/chain'.format(node)
			try:
				response = requests.get(url)
				node_chain = response.json()
				node_chain = [Block.from_dict(block) for block in node_chain]
				node_chain_length = len(node_chain)
				local_chain_length = len(self.__chain)
				if node_chain_length > local_chain_length and Verification.verify_chain(node_chain, self.mining_difficulty):
					winner_chain = node_chain
					replace = True
			except requests.exceptions.ConnectionError:
				continue
		self.resolve_conflicts = False
		if replace:
			self.__chain = winner_chain
			self.__open_transactions = []		# Invalidate any previously open transactions
			self.save_data()
		return replace


	def get_peer_nodes(self):
		"""Returns a list of connected peer nodes"""
		return list(self.__peer_nodes)


	def add_peer_node(self, node):
		"""Adds a new node to the set of connected peer nodes

		Arguments:
			:node: The peer node URL to be added
		"""
		self.__peer_nodes.add(node)
		self.save_data()


	def remove_peer_node(self, node):
		"""Removes a node from the set of connected peer nodes

		Arguments:
			:node: The peer node URL to be removed
		"""
		self.__peer_nodes.discard(node)
		self.save_data()


	def broadcast(self, endpoint, data):
		"""Generic function for broadcasting data to all active nodes"""
		for node in self.__peer_nodes:
			url = 'http://{}/{}'.format(node, endpoint)
			try:
				response = requests.post(url, json=data)
				if response.status_code == 409:
					self.resolve_conflicts = True
					return False
				elif response.status_code >= 400:
					# TODO: print('Transaction declined, needs resolving')
					return False
			except requests.exceptions.ConnectionError:
				# Node is offline?
				continue
		return True

