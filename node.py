from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
CORS(app)

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)



def validate_request_data(data, required_fields=None):
	"""Helper function to validates the request data.
	returns None if data is valid, i.e., data is present and
	required_fields, if any, are also present.
	Otherwise, returns a jsonify() response object with 400 status.

	Arguments:
		:data: Dictionary of request parameters to validate
		:required_fields: List of fields that are required to be present
	"""
	if not data:
		response = {'message': 'No data found'}
		return jsonify(response), 400
	if required_fields:
		if not all(field in data for field in required_fields):
			response = {'message': 'Required data is misssing'}
			return jsonify(response), 400
	return None



@app.route('/', methods=['GET'])
def get_ui():
	return send_from_directory('ui', 'node.html')

@app.route('/network', methods=['GET'])
def get_network_ui():
	return send_from_directory('ui', 'network.html')


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

	data = request.get_json()
	required_fields = ['recipient', 'amount']
	invalid_data_response = validate_request_data(data, required_fields)
	if invalid_data_response:
		return invalid_data_response

	recipient = data['recipient']
	amount = data['amount']
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


@app.route('/broadcast_transaction', methods=['POST'])
def broadcast_transaction():
	"""Receive broadcast of newly added transactions from other nodes"""
	data = request.get_json()
	required_fields = ['sender', 'recipient', 'amount', 'signature']
	invalid_data_response = validate_request_data(data, required_fields)
	if invalid_data_response:
		return invalid_data_response

	success = blockchain.add_transaction(sender=data['sender'], recipient=data['recipient'], amount=data['amount'], signature=data['signature'], is_receiving=True)
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


@app.route('/broadcast_block', methods=['POST'])
def broadcast_block():
	"""Receive broadcast of newly mined blocks from other nodes"""
	data = request.get_json()
	required_fields = ['block']
	invalid_data_response = validate_request_data(data, required_fields)
	if invalid_data_response:
		return invalid_data_response

	block = data['block']
	last_local_block_index = blockchain.get_last_block()['index']
	if block['index'] == last_local_block_index + 1:
		if blockchain.add_block(block):
			response = {'message': 'Block added successfully'}
			return jsonify(response), 201
		else:
			response = {'message': 'Block seems invalid'}
			return jsonify(response), 500
	elif block['index'] > last_local_block_index:
		pass
	else:
		# Our blockchain is more recent (has longer chain)
		response = {'message': 'Bockchain seems to be shorter. Block not added'}
		return jsonify(response), 409	# Invalid data


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


@app.route('/nodes', methods=['GET'])
def get_nodes():
	response = {
		'peer_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 200


@app.route('/node', methods=['POST'])
def add_node():
	data = request.get_json()
	required_fields = ['node']
	invalid_data_response = validate_request_data(data, required_fields)
	if invalid_data_response:
		return invalid_data_response

	blockchain.add_peer_node(data['node'])
	response = {
		'message': 'Node added successfully',
		'peer_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 201


@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
	if not node_url:
		response = {
			'message': 'No node data found'
		}
		return jsonify(response), 400
	blockchain.remove_peer_node(node_url)
	response = {
		'message': 'Node removed successfully',
		'peer_nodes': blockchain.get_peer_nodes()
	}
	return jsonify(response), 200



if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-p', '--port', type=int, default=4000)
	args = parser.parse_args()
	app.run(host='127.0.0.1', port=args.port)
