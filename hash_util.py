import hashlib
import json


def hash_str_256(str):
	"""Returns SHA256 hash of a string as string

	Arguments:
		:str: The string to hash
	"""
	return hashlib.sha256(str).hexdigest()


def hash_block(block):
	"""Returns the SHA256 hash of the block as a string

	Arguments:
		:block: The block to hash
	"""
	# Convert string to UTF8 with encode()
	# Return string representation of SHA256 with hexdigest()
	# The "sort_keys=True" ensures that order of data remains same during multiple hashing of same block
	return hash_str_256(json.dumps(block, sort_keys=True).encode())
