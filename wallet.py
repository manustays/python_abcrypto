from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii


class Wallet:

	def __init__(self):
		self.private_key = None
		self.public_key = None


	def create_keys(self):
		private_key, public_key = self.generate_keys()
		self.private_key = private_key
		self.public_key = public_key


	def save_keys(self):
		if self.public_key != None and self.private_key != None:
			try:
				with open('wallet_store.txt', mode='w') as f:
					f.write(self.public_key)
					f.write('\n')
					f.write(self.private_key)
					return True
			except (IOError, IndexError):
				return False
		else:
			return False


	def load_keys(self):
		try:
			with open('wallet_store.txt', mode='r') as f:
				keys = f.readlines()
				self.public_key = keys[0][:-1]
				self.private_key = keys[1]
				return True
		except (IOError, IndexError):
			return False


	def generate_keys(self):
		private_key = RSA.generate(1024, Crypto.Random.new().read)
		public_key = private_key.publickey()
		return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))


	def sign_transactions(self, sender, recipient, amount):
		"""Returns a cryptographic signature for the transaction using sender's private-key"""
		signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
		payload_hash = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
		signature = signer.sign(payload_hash)
		return binascii.hexlify(signature).decode('ascii')


	@staticmethod
	def verify_transaction_signature(transaction):
		public_key = RSA.importKey(binascii.unhexlify(transaction.sender))	# transaction.sender is the public key of the sender
		verifier = PKCS1_v1_5.new(public_key)
		payload_hash = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
		return verifier.verify(payload_hash, binascii.unhexlify(transaction.signature))