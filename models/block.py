from .location import Location
from .product import Product
from hashlib import sha256
import json

class Block:
    def __init__(self, index, transactionType, product, timestamp, previousHash, ownerRelation, location, nonce=0):
        self.index = index
        self.transactionType = transactionType
        self.product = product
        self.timestamp = timestamp
        self.previousHash = previousHash
        self.ownerRelation = ownerRelation
        self.location = location
        self.nonce = nonce

    def computeHash(self):
        blockString = json.dumps(self, default=lambda x: x.__dict__, sort_keys=True)
        return sha256(blockString.encode()).hexdigest()