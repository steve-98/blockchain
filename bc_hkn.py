import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
    
    
        #create a genesis block(the block to start everything out)
        self.new_block(previous_hash=1, proof=100)
        
        
    def new_block(self, proof, previous_hash=None):
        """
        Creates a new block and adds it to the blockchain.
        
        Args:
            proof (int): The proof of work for the new block.
            previous_hash (str, optional): The hash of the previous block in the blockchain. Defaults to None.
        
        Returns:
            dict: The new block that was created and added to the blockchain.
        """
        block={
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        #reset the current list of transactions????
        
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self,sender, recipient, amount):
        #adds a new transaction to the list of transactions
        """
        Adds a new transaction to the list of transactions.
        
        Args:
            sender (str): The sender of the transaction.
            recipient (str): The recipient of the transaction.
            amount (float): The amount of the transaction.
        """
        self.current_transactions.append({
           'sender': sender,
           'recipient': recipient,
            'amount': amount
        })
        
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        #hashes a block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
        pass
    
    @property
    def last_block(self):
        #returns the last block in the chain
        return self.chain[-1]
    
    #creating new transactions and adding them to a block
    
    def new_transaction(self, sender, recipient, amount):
        #creates a new transaction to go into the next mined block
        #sender=address of the sender
        #recipient=address of the recipient
        #amount=amount of the transaction
        #return the index of the block that will hold this transaction
        self.current_transactions.append({
           'sender': sender,
           'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1
    
    #implimenting the proof of work algo
    def proof_of_work(self, last_proof):
        #simple algo to find a number p such that hash(pp') contains 4 leading zeroes
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

#the app code to turn the blockchain into an api

app = Flask(__name__)

#generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

#instanciate the bc
blockchain = Blockchain()

#define the routes that the app will have

@app.route('/mine', methods=['GET'])
def mine():
    
    #running the proof of work to generater the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    #impliment reward for finding the proof, the sender becomes'0' to show that this is a new mined coin
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    #add the new block to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    response = {
       'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    
    values=request.get_json()
    
    required = ['sender','recipient', 'amount']
    if not all (k in values for k in required):
        return 'Missing values', 400
    
    #create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# Starts the Flask application and listens for incoming requests on the specified host and port.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)