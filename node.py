#!/usr/bin/env python3

# from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification


class Node:

	def __init__(self):
		# self.id = str(uuid4())
		self.id = 'Abhi'
		self.blockchain = Blockchain(self.id)


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
		print()
		print("-" * 20)
		print("  SELECT AN OPTION")
		print("-" * 20)
		print("1. Add New Transaction")
		print("2. Mine Blockchain")
		print("3. View Blockchain")
		print("4. View My Balance")
		print("5. Verify Open Transactions")
		print("m. Manipulate Blockchain")
		print("q. Quit")
		return input('Enter your choice: ')


	def command_line_interface(self):
		"""Take user input on a command line in a loop until the user quits"""
		take_user_input = True
		while take_user_input:
			user_choice = self.get_user_choice()

			print()

			if user_choice == '1':
				recipient, amount = self.get_transaction_details()
				if self.blockchain.add_transaction(sender=self.id, recipient=recipient, amount=amount):
					print("Transaction Added.")
				else:
					print("Transaction Failed!")
				print("\nOpen Transactions: ", self.blockchain.get_open_transactions())

			elif user_choice == '2':
				self.blockchain.mine_block()
				print("\nBalance of {}: {:6.2f}".format(self.id, self.blockchain.get_balance()))

			elif user_choice == '3':
				self.print_blockchain_elements()

			elif user_choice == '4':
				print("\nBalance of {}: {:6.2f}".format(self.id, self.blockchain.get_balance()))

			elif user_choice == '5':
				if Verification.verify_open_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
					print("\nAll open transactions are valid.")
				else:
					print("\nSome open transactions are invalid!")
				print("Open Transactions: ", self.blockchain.get_open_transactions())

			elif user_choice == 'm':
				if len(self.blockchain.get_chain()) > 0:
					self.blockchain.get_chain()[0] = {
						'previous_hash': '',
						'index': 0,
						'transactions': [{'sender': 'Amit', 'recipient': 'Abhi', 'amount':100.0}]
					}

			elif user_choice == 'q' or user_choice == '0':
				take_user_input = False

			else:
				print('Invalid choice!')

			if not Verification.verify_chain(self.blockchain.get_chain(), self.blockchain.mining_difficulty):
				print('Invalid Blockchain!!')
				take_user_input = False


# Start UI on a command-line-interface only if this file was executed directly
if __name__ == '__main__':
	node = Node()
	node.command_line_interface()
