blockchain = [[1]]


def get_last_blockchain_value():
    return blockchain[-1]


def add_value(transaction_amount):
    blockchain.append([get_last_blockchain_value(), transaction_amount])
    # print(blockchain)


def get_user_amount():
    return float(input('Enter the transaction amount: '))


add_value(get_user_amount())
add_value(get_user_amount())
add_value(get_user_amount())

print("Blockchain: ", blockchain)
