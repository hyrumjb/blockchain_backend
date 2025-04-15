from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import datetime as date
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://blockchain_backend_user:SaxuQIhBJakZdrQ9m4tMJkDKGjjtTrEm@dpg-cvunuic9c44c738c1a20-a.oregon-postgres.render.com/blockchain_backend")

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class BlockModel(Base):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    timestamp = Column(String)
    data = Column(Text)
    hash = Column(String)
    previous_hash = Column(String)

Session = sessionmaker(bind=engine)

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
        
def load_blockchain():
    session = Session()
    block_models = session.query(BlockModel).order_by(BlockModel.index).all()
    session.close()
    return [
        Block(
            b.index, b.timestamp, b.data, b.previous_hash, b.hash
        ) for b in block_models
    ]

def save_block(block):
    session = Session()
    block_model = BlockModel(
        index=block.index,
        timestamp=block.timestamp,
        data=block.data,
        hash=block.hash,
        previous_hash=block.previous_hash
    )
    session.add(block_model)
    session.commit()
    session.close()

blockchain = load_blockchain()
if not blockchain:
    genesis_block = Block(0, str(date.datetime.now()), "Genesis Block", "0")
    blockchain = [genesis_block]
    save_block(genesis_block)

@app.route("/blockchain")
def get_blockchain():
    chain = load_blockchain()
    return jsonify([
        {
            'index': b.index,
            'timestamp': b.timestamp,
            'data': b.data,
            'hash': b.hash,
            'previous_hash': b.previous_hash
        } for b in chain
    ])

@app.route("/add-block", methods=["POST"])
def add_block():
    chain = load_blockchain()
    latest_block = chain[-1]
    new_index = latest_block.index + 1
    new_data = request.json.get("data", f"Transaction Data {new_index}")
    new_timestamp = str(date.datetime.now())
    new_block = Block(new_index, new_timestamp, new_data, latest_block.hash)
    save_block(new_block)
    return jsonify({"message": f"Block #{new_index} added!"})

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    if not load_blockchain():
        genesis_block = Block(0, str(date.datetime.now()), "Genesis Block", "0")
        save_block(genesis_block)
    
    app.run(debug=True)