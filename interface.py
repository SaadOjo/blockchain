import requests
import json
import socket
from blockchain import Blockchain


class Interface(object):

    def __init__(self):
        self.blockchain = Blockchain()

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def mine(self):  # add min transactions requirement (added in main program)
        # We run the proof of work algorithm to get the next proof...
        self.update_current_transactions()  # make sure to collect transactions from other nodes

        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.blockchain.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.blockchain.new_transaction(
            sender="0",
            recipient=self.blockchain.address,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }

        print(response)

    def update_nodes(self):

        ip = self.get_ip()
        ip_prefix = ip[:10]
        for x in range(0, 255):  # would not include you as flask hasn't started yet
            url = f'http://{ip_prefix}{x}:5000/address'
            try:
                response = requests.get(url, timeout=0.01)
                if response.status_code == 200:
                    address = response.json()['address']
                    if address != self.blockchain.address:
                        self.blockchain.register_node(url, address)
                        # tell other nodes about you
                        node_data = {
                            'url': f'{ip_prefix}{x}:5000',
                            'address': self.blockchain.address,
                        }
                        try:
                            requests.post(f'http://{ip_prefix}{x}:5000/register_node', json.dumps(node_data))
                        except requests.exceptions.ConnectionError:
                            print(f'failed to register this node at {ip_prefix}{x} ')

            except requests.exceptions.ConnectionError:
                print(f'no node {url}')

        response = {
            'message': 'List of nodes',
            'total_nodes': list(self.blockchain.nodes),
        }

        print(response)

    def consensus(self):
        replaced = self.blockchain.resolve_conflicts()

        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': self.blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': self.blockchain.chain
            }

        print(response)

    def send(self, address, amount):

        # Create a new Transaction
        if self.blockchain.my_balance() >= amount:  # also check current transactions
            index = self.blockchain.new_transaction(self.blockchain.address, address, amount)
            response = {'message': f'Transaction will be added to Block {index}'}
            print(response)
        else:
            print('you do not have enough balance to make this transaction:')

    def update_current_transactions(self):

        for nodes in self.blockchain.nodes:
            url = nodes[0]
            response = requests.get(f'http://{url}/transactions')

            if response.status_code == 200:
                current_transactions = response.json()['transactions']
                for transaction in current_transactions:
                    unique_transaction = True
                    for my_transactions in self.blockchain.current_transactions:
                        if transaction['time'] == my_transactions['time']:
                            unique_transaction = False

                    if unique_transaction == True:
                        self.blockchain.current_transactions.append(transaction)
