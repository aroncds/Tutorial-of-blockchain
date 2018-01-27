import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from urlib.parse import urlparse
import requests

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        print(self.chain)
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

    def new_transactions(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain)
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n---------------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof'])
                return False
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    @staticmethod

    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"

    def hash(self, block):
        print(self)
        print(block)
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property

    def last_block(self):
        return self.chain[-1]


app = Flask(__name__)
node_identifire = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Node list is invalid!!", 400

    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': 'Append new node !!',
        total_nodes: list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Chain is replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Chain is confirmed',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transactions(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction is append in the block {index}'}
    return jsonify(response), 201

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']

    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transactions(
        sender='0',
        recipient=node_identifire,
        amount=1,
    )
    block = blockchain.new_block(proof)

    response = {
        'message': 'Mined new block!!',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
