import hashlib
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
import json


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()
        self.address = str(uuid4()).replace('-', '')

    def register_node(self, url, address):
        """
        Add a new node to the list of nodes
        :param url:
        :param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
        :return: None
        """

        parsed_url = urlparse(url)
        node = (parsed_url.netloc, address)
        self.nodes.add(node)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:

            node_url = node[0]
            response = requests.get(f'http://{node_url}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        transaction = {
            'sender':sender,
            'recipient': recipient,
            'amount': amount,
            'time': time(),
            }

        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1

    def my_balance(self):
        my_balance = 0

        for block in self.chain:
            transactions = block['transactions']
            for transaction in transactions:
                recipient = transaction['recipient']  # test
                sender = transaction['sender']
                if recipient == self.address:
                    my_balance += transaction['amount']
                if sender == self.address:
                    my_balance -= transaction['amount']

        return my_balance

    def proof_of_work(self, last_proof):

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        # Hashes a Block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
