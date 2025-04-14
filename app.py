from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import datetime as date

app = Flask(__name__)
CORS(app, supports_credentials=True)

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        hash_string = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)
        return hashlib.sha256(hash_string.encode()).hexdigest()
        
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, date.datetime.now(), "Genesis Block", "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def to_dict(self):
        return [
            {
                'index': block.index,
                'timestamp': str(block.timestamp),
                'data': block.data,
                'hash': block.hash,
                'previous_hash': block.previous_hash
            }
            for block in self.chain
        ]

blockchain = Blockchain()
# for i in range(1, 16):
#     blockchain.add_block(Block(i, date.datetime.now(), f"Transaction Data {i}", ""))

@app.route("/blockchain")
def get_blockchain():
    return jsonify(blockchain.to_dict())

@app.route("/add-block", methods=["POST"])
def add_block():
    global blockchain
    new_index = len(blockchain.chain)
    new_data = f"Transaction Data {new_index}"
    new_block = Block(new_index, date.datetime.now(), new_data, "")
    blockchain.add_block(new_block)
    return jsonify({"message": f"Block #{new_index} added!"})

if __name__ == '__main__':
    app.run(debug=True)
