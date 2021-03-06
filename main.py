from flask import Flask, jsonify, request
import json
from interface import Interface
import _thread
import sys

#dummy comment

# tell other nodes on making a transaction

# add requests

interface = Interface()
# Instantiate our Node
# main program runs here


def mine():
    if len(interface.blockchain.current_transactions) >= 2:
        interface.mine()
    else:
        print('not enough transactions in the AIR to mine')


print('Client Started')
interface.update_nodes()
interface.consensus()
mine()



def cli():
    while True:
        userinput = input('>> ')
        splitinput = userinput.split()

        if splitinput:

            if splitinput[0] == 'balance':
                interface.consensus()
                balance = interface.blockchain.my_balance()
                print(f'your balance is: {balance} coins.')

            if splitinput[0] == 'update_blockchain':
                interface.consensus()
                print(f'blockchain updated.')

            elif splitinput[0] == 'mine':
                interface.update_current_transactions()
                mine()

            elif splitinput[0] == 'chain': # cheat codes
                print(interface.blockchain.chain)

            elif splitinput[0] == 'rich':
                interface.blockchain.new_transaction(0, interface.blockchain.address, 100)
                interface.mine()
                print('you are now rich. Check your balance to confirm.')

            elif splitinput[0] == 'update_nodes':
                interface.update_nodes()

            elif splitinput[0] == 'exit':
                print('Terminating Program')
                sys.exit()

            elif splitinput[0] == 'nodes':

                if len(interface.blockchain.nodes) == 0:
                    print('there are no other nodes in the network')

                else:
                    i = 1
                    for nodes in interface.blockchain.nodes:
                        node_address = nodes[1]
                        print(f'{i}) {node_address}')

            elif splitinput[0] == 'send':
                receiver = splitinput[1][6:]
                print(f'the receiver is: {receiver}\n')
                amount = float(splitinput[2][6:])
                print(f'the amount is: {amount}\n')
                response = input('Y/N?')
                if response == 'Y':
                    interface.send(receiver, amount)
                elif response == 'N':
                    print('Transaction Discarded!')

            elif splitinput[0] == 'help':
                print('This program has the following functions:\n')
                print('1) balance (Check your ether balance)\n')
                print('2) send    (send money to someone) EX: send addr--0x123456789 amnt--25 \n')
                print('3) nodes   (Show the address of nodes in the network)\n')
                print('4) mine    (update the blockchain)\n')
                print('5) exit    (exit the program)\n')
                print('The Programs automatically mines periodically to maintain the blockchain (not currently)\n')


app = Flask(__name__)


@app.route('/address', methods=['GET'])
def show_address():
    response = {
        'address': interface.blockchain.address,
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': interface.blockchain.chain,
        'length': len(interface.blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions', methods=['GET'])
def current_transactions():
    response = {
        'transactions': interface.blockchain.current_transactions,
    }
    return jsonify(response), 200


@app.route('/register_node', methods=['POST'])
def register_node():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['url', 'address']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    interface.blockchain.register_node(values['url'], values['address'])

    response = {'message': f'node registered'}
    return jsonify(response), 201


if __name__ == '__main__':
    _thread.start_new_thread(cli, ())
    print('****SAAD COIN****\n')
    print('Create by Syed Saad Saif\n')
    print('************************\n')
    print('Command Line Interface:\n')
    app.run(host='0.0.0.0', port=5000)

