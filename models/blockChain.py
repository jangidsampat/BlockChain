from .block import Block
from .ownerRelation import OwnerRelation
from .product import Product
from .location import Location
import time

class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmedTransactions = []
        self.chain = []
        self.prodId = 1

    def createGenesisBlock(self):
        genesisBlock = Block(0, 1, Product(0, 0, False), 0, 0, OwnerRelation("0", "0", -1), Location(0, 0), "0")
        genesisBlock.hash = genesisBlock.computeHash()
        self.chain.append(genesisBlock)

    @property
    def lastBlock(self):
        return self.chain[-1]

    def addBlock(self, block, proof):
        previousHash = self.lastBlock.hash
        if previousHash != block.previousHash:
            return False
        if not Blockchain.isValidProof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def addUser(self):
        pass

    @staticmethod
    def proofOfWork(block):
        block.nonce = 0
        computedHash = block.computeHash()
        while not computedHash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computedHash = block.computeHash()
        return computedHash

    def addNewTransaction(self, transaction, transacType):
        if transacType==1:
            transaction.product.productId = self.prodId
            self.prodId+=1
        self.unconfirmedTransactions.append(transaction)

    @classmethod
    def isValidProof(cls, block, blockHash):
        return (blockHash.startswith('0' * Blockchain.difficulty) and
                blockHash == block.computeHash())

    @classmethod
    def checkChainValidity(cls, chain):
        result = True
        previousHash = "0"
        for block in chain:
            blockHash = block.hash
            delattr(block, "hash")
            if not cls.isValidProof(block, blockHash) or \
                    previousHash != block.previousHash:
                result = False
                break
            block.hash, previousHash = blockHash, blockHash
        return result

    def mine(self):
        if not self.unconfirmedTransactions:
            return False
        lastBlock = self.lastBlock
        newBlock = Block(index=lastBlock.index + 1,
                         transactionType=self.unconfirmedTransactions[0].transactionType,
                          product=self.unconfirmedTransactions[0].product,
                          timestamp=self.unconfirmedTransactions[0].timestamp,
                          ownerRelation=self.unconfirmedTransactions[0].ownerRelation,
                          location=self.unconfirmedTransactions[0].location,
                          previousHash=lastBlock.hash)
        proof = self.proofOfWork(newBlock)
        self.addBlock(newBlock, proof)
        self.unconfirmedTransactions = []
        return True