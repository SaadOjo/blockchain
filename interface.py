import requests
from blockchain import Blockchain


class Interface(object):

    def __init__(self):
        self.blockchain = Blockchain()

    def mine(self):  # add min transactions requirement
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

        for x in range(120, 125):  # would not include you as flask hasn't started yet
            url = f'http://192.168.1.{x}:5000/address'

            try:
                response = requests.get(url, timeout=0.1)
                if response.status_code == 200:
                    address = response.json()['address']
                    self.blockchain.register_node(url, address)
                    print(f'node found at {url}')

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
        if self.blockchain.my_balance() >= amount:
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
                        self.blockchain.current_transactions.add(transaction)
