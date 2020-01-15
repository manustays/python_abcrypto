import hashlib
import json


def hash_str_256(str):
	"""Returns SHA256 hash of a string as string

	Arguments:
		:str: The string to hash
	"""
	# Return string representation of SHA256 using hexdigest()
	return hashlib.sha256(str).hexdigest()


def hash_block(block):
	"""Returns the SHA256 hash of the block as a string

	Arguments:
		:block: The block to hash. It's an object of class Block
	"""
	# Convert string to UTF8 with encode()
	# The "sort_keys=True" ensures that order of data remains same during multiple hashing of same block
	hashable_block = block.__dict__.copy()
	hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
	return hash_str_256(json.dumps(hashable_block, sort_keys=True).encode())
