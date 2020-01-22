from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
CORS(app)

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)



@app.route('/', methods=['GET'])
def get_ui():
	return send_from_directory('ui', 'node.html')


@app.route('/transactions', methods=['GET'])
def get_transactions():
	transactions = blockchain.get_open_transactions()
	dict_transactions = [tx.to_dict() for tx in transactions]
	return jsonify(dict_transactions), 200


@app.route('/transaction', methods=['POST'])
def add_transaction():
	"""TODO: Validate input parameters"""
	if wallet.public_key == None:
		response = {
			'message': 'No wallet set up.'
		}
		return jsonify(response), 400
	values = request.get_json()
	if not values:
		response = {
			'message': 'No data found'
		}
		return jsonify(response), 400
	required_fields = ['recipient', 'amount']
	if not all(field in values for field in required_fields):
		response = {
			'message': 'Required data is misssing'
		}
		return jsonify(response), 400
	recipient = values['recipient']
	amount = values['amount']
	signature = wallet.sign_transactions(wallet.public_key, recipient, amount)
	success = blockchain.add_transaction(sender=wallet.public_key, recipient=recipient, amount=amount, signature=signature)
	if success:
		response = {
			'message': 'Transaction added successfully.',
			'transaction': blockchain.get_open_transactions()[-1].to_dict(),
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to create a transaction'
		}
		return jsonify(response), 500


@app.route('/wallet', methods=['POST'])
def create_keys():
	wallet.create_keys()
	if wallet.save_keys():
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		response = {
			'public_key': wallet.public_key,
			'private_key': wallet.private_key,
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Failed to save the wallet keys.'
		}
		return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
	if wallet.load_keys():
		global blockchain
		blockchain = Blockchain(wallet.public_key)
		response = {
			'public_key': wallet.public_key,
			'private_key': wallet.private_key,
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 200
	else:
		response = {
			'message': 'Failed to load the wallet keys.'
		}
		return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
	balance = blockchain.get_balance()
	if balance != None:
		response = {
			'message': 'Balance fetched successfully',
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 200
	else:
		response = {
			'message': 'Failed to load balance.',
			'is_wallet_setup': wallet.public_key != None
		}
		return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
	block = blockchain.mine_block()
	if block != None:
		response = {
			'message': 'Mining successful. Block added.',
			'added_block': block.to_dict(),
			'balance': blockchain.get_balance()
		}
		return jsonify(response), 201
	else:
		response = {
			'message': 'Mining failed. Block not added.',
			'is_wallet_setup': wallet.public_key != None
		}
		return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
	return jsonify(blockchain.get_chain_dict()), 200



if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000)
