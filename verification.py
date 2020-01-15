from hash_util import hash_block, hash_str_256

class Verification:

	@staticmethod
	def valid_proof(transactions, last_hash, proof, POW_LEADING_ZEROS):
		"""Returns True, if the proof (nonce) is valid a proof-of-work,
		i.e., if it satisfies the proof-of-work condition of generating
		a hash with the pre-defined number of zeros.

		Arguments:
			:transactions: List of transactions of the block for which proof is required
			:last_hash: Hash of last block stored in the current block
			:proof: The Nonce number that is to be checked
		"""
		guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()	# Combine and UTF8 encode
		guess_hash = hash_str_256(guess)
		# print("GUESS HASH: ", guess_hash)
		return guess_hash[:POW_LEADING_ZEROS] == ('0' * POW_LEADING_ZEROS)


	@classmethod
	def verify_chain(cls, blockchain, POW_LEADING_ZEROS):
		"""Verifies the blockchain and returns True if it is valid, False otherwise"""
		for (index,block) in enumerate(blockchain):
			if index == 0:
				# Ignore the Genesis block.
				continue
			if block.previous_hash != hash_block(blockchain[index-1]):
				# Fail verification, if the previous-hash stored in the block does not match
				# the actual hash of the previous block.
				print(f"ERROR: The previous-hash in block {index} does not match the actual hash")
				return False
			if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof, POW_LEADING_ZEROS):
				# Fail verification, if the proof-of-work is invalid,
				# i.e, it does not generate the required hash from the stored proof.
				# Ignore the last transaction in the transactions array, which is the mining reward
				print(f"ERROR: The proof-of-work in block {index} is invalid")
				return False
		# Verify the blockchain, if it did not fail anywhere in the previous loop
		return True


	@staticmethod
	def verify_transaction(transaction, get_balance):
		"""Returns True if the Sender of the transaction has sufficient balance for the transaction

		Arguments:
			:transaction: The transaction to verify (object of class Transaction)
		"""
		sender_balance = get_balance()
		return sender_balance >= transaction.amount


	@classmethod
	def verify_open_transactions(cls, open_transactions, get_balance):
		"""Verifies all open-transactions and returns True if all are valid, False otherwise"""
		return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])