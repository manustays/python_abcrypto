#!/usr/bin/env python3

# from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet


class Node:

	def __init__(self):
		# self.wallet = str(uuid4())
		self.wallet = Wallet()
		self.blockchain = None


	def get_transaction_details(self):
		"""Inputs the transaction details (recipient & amount) from the user and returns it"""
		tx_recipient = input('Enter the recipient of the transaction: ')
		tx_amount =  float(input('Enter the transaction amount: '))
		return (tx_recipient, tx_amount)


	def print_blockchain_elements(self):
		"""Print all the blocks of the blockchain"""
		for block in self.blockchain.get_chain():
			print("Block: ", block)


	def get_user_choice(self):
		"""Inputs a choice from the user"""
		wallet_loaded = self.wallet.public_key != None and self.blockchain != None
		print("\n\n")
		print("=" * 40)
		if wallet_loaded:
			print("WALLET PUBLIC KEY: ", self.wallet.public_key)
			print("BALANCE: {:.2f}".format(self.blockchain.get_balance()))
		else:
			print("[No Wallet Loaded]")
		print("-" * 40)
		print("  SELECT AN OPTION")
		print("-" * 20)
		if wallet_loaded:
			print("1. Add New Transaction")
			print("2. Mine Blockchain")
			print("3. View Blockchain")
			print("4. Verify Open Transactions")
		print("5. Create Wallet")
		print("6. Load Wallet")
		if wallet_loaded: print("7. Save Wallet")
		print("q. Quit")
		return input('Enter your choice: ')


	def command_line_interface(self):
		"""Take user input on a command line in a loop until the user quits"""
		take_user_input = True
		while take_user_input:
			user_choice = self.get_user_choice()

			print()

			if user_choice == '1':
				# Add transaction
				recipient, amount = self.get_transaction_details()
				signature = self.wallet.sign_transactions(sender=self.wallet.public_key, recipient=recipient, amount=amount)
				if self.blockchain.add_transaction(sender=self.wallet.public_key, recipient=recipient, amount=amount, signature=signature):
					print("Transaction Added.")
				else:
					print("Transaction Failed!")
				print("\nOpen Transactions: ", self.blockchain.get_open_transactions())

			elif user_choice == '2':
				# Mine block
				print("\nMining started...")
				proof = self.blockchain.mine_block()
				if proof != False:
					print("Mining done! Proof={}, Balance={:.2f}".format(proof, self.blockchain.get_balance()))
				else:
					print("Mining failed!")

			elif user_choice == '3':
				# Print blockchain
				self.print_blockchain_elements()

			elif user_choice == '4':
				# Verify open transactions
				if Verification.verify_open_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
					print("\nAll open transactions are valid.")
				else:
					print("\nSome open transactions are invalid!")
				print("Open Transactions: ", self.blockchain.get_open_transactions())

			elif user_choice == '5':
				# Create wallet
				self.wallet.create_keys()
				self.blockchain = Blockchain(self.wallet.public_key)
				print("\nNew Wallet Created. Public key:", self.wallet.public_key)

			elif user_choice == '6':
				# Load wallet
				if self.wallet.load_keys() == True:
					self.blockchain = Blockchain(self.wallet.public_key)
					print("\nWallet Loaded from save-file. Public key:", self.wallet.public_key)
				else:
					print("\nFailed to load Wallet from save-file!")

			elif user_choice == '7':
				# Save wallet
				if self.wallet.save_keys() == True:
					print("\nWallet saved to file.")
				else:
					print("\nFailed to save Wallet to file!")

			elif user_choice == 'q' or user_choice == '0':
				take_user_input = False

			else:
				print('Invalid choice!')

			if self.blockchain and not Verification.verify_chain(self.blockchain.get_chain(), self.blockchain.mining_difficulty):
				print('Invalid Blockchain!!')
				take_user_input = False


# Start UI on a command-line-interface only if this file was executed directly
if __name__ == '__main__':
	node = Node()
	node.command_line_interface()
