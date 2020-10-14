from models.blockChain import Blockchain
from models.block import Block
from models.ownerRelation import OwnerRelation
from models.owner import Owner
from models.location import Location
from models.product import Product
from flask import Flask, request
from hashlib import sha256
import bcrypt
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
import requests
import os
import datetime
import time
import json

app = Flask(__name__)

aesKey = 'ffffffffffffffffffffffffffffffff'
blockchain = Blockchain()
blockchain.createGenesisBlock()
peers = set()
users = {}

#*********************** POST **************************
@app.route('/newTransaction', methods=['POST'])
def newTransaction():
    txData = request.get_json()
    print(txData)
    transacType = int(txData.get('transacType'))
    tempUser = users[txData.get('username')]
    tempPK = tempUser.publicKey
    tempPK = tempPK.replace("-----BEGIN PUBLIC KEY-----", "")
    tempPK = tempPK.replace(os.linesep, "")
    tempPK = tempPK.replace("-----END PUBLIC KEY-----", "")
    newBlock = Block(0,
                     transacType,
                     Product(int(txData.get('prodId')), int(txData.get('productType')), False),
                     timeStampToString(),
                     0,
                     OwnerRelation(tempPK, tempUser.username, tempUser.userType),
                     Location(float(txData.get('latitude')), float(txData.get('longitude'))),
                     0)
    blockchain.addNewTransaction(newBlock, transacType)
    return "Success", 200


@app.route('/registerNode', methods=['POST'])
def registerNewPeers():
    nodeAddress = request.get_json()["nodeAddress"]
    if not nodeAddress:
        return "Invalid data", 400
    peers.add(nodeAddress)
    if request.host_url in peers:
        peers.remove(request.host_url)
    print("The Other Side : ", peers)
    return getChain()


@app.route('/registerWith', methods=['POST'])
def registerWithExistingNode():
    nodeAddress = request.get_json()["nodeAddress"]
    if not nodeAddress:
        return "Invalid data", 400
    data = {"nodeAddress": request.host_url}
    headers = {'Content-Type': "application/json"}
    response = requests.post(nodeAddress + "/registerNode", data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        chainDump = response.json()['chain']
        blockchain = createChainFromDump(chainDump)
        peers.update(response.json()['peers'])
        peers.add(nodeAddress)
        if request.host_url in peers:
            peers.remove(request.host_url)
        print("Host Side : ", peers)
        return "Registration successful", 200
    else:
        return response.content, response.status_code


@app.route('/addBlock', methods=['POST'])
def verifyAndAddBlock():
    blockData = request.get_json()['chain']
    block = Block(blockData["index"],
                  blockData["transactionType"],
                  Product(blockData["product"]["productId"], blockData["product"]["productType"], blockData["product"]["isCertified"]),
                  blockData["timestamp"],
                  blockData["previous_hash"],
                  OwnerRelation(blockData["ownerRelation"]["ownerKey"], blockData["ownerRelation"]["name"], blockData["ownerRelation"]["relType"]),
                  Location(blockData["location"]["lat"], blockData["location"]["lng"]),
                  blockData["nonce"])

    proof = blockData['hash']
    added = blockchain.addBlock(block, proof)
    blockchain.prodId = int(request.get_json()['prodId'])

    if not added:
        return "The block was discarded by the node", 400
    return "Block added to the chain", 201


@app.route('/addUser', methods=['POST'])
def addUser():
    global aesKey
    userData = request.get_json()
    if userData['username'] in users:
        return "User already Exists", 400
    
    key = RSA.generate(2048)
    publicKey = str(key.publickey().export_key(), 'utf-8')
    privateKey = str(key.export_key(), 'utf-8')
    user = Owner(publicKey,
                 privateKey,
                 userData["type"],
                 userData["name"],
                 hashPassword(userData["password"]),
                 userData["username"])
    users[user.username] = user
    return "User Created", 200


@app.route('/syncClient', methods=['POST'])
def syncClient():
    userData = request.get_json()
    user = Owner(userData['publicKey'],
                 userData['privateKey'],
                 userData['type'],
                 userData['name'],
                 userData['password'],
                 userData['username'])
    users[userData['username']] = user
    return "Done", 200

@app.route('/syncHost', methods=['POST'])
def syncHost(user):
    for peer in peers:
        url = "{}syncClient".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(user),
                      headers=headers)
    return "Done", 200


@app.route('/loginUser', methods=['POST'])
def loginUser():
    userData = request.get_json()
    if userData["username"] not in users:
        return "User not Found", 400
    if users[userData["username"]].password == hashPassword(userData["password"]):
        return json.dumps({'user': json.dumps(users[userData["username"]], default=lambda x: x.__dict__, sort_keys=True)}), 200
    return "Wrong Username or Passwrod", 400


#************************ GET **************************
@app.route('/chain', methods=['GET'])
def getChain():
    chainData = []
    userData = []
    for block in blockchain.chain:
        chainData.append(json.dumps(block, default=lambda x: x.__dict__, sort_keys=True))
    for user in users.values():
        userData.append(json.dumps(user, default=lambda x: x.__dict__, sort_keys=True))
    return {"length": len(chainData),
            "chain": chainData,
            "users": userData,
            "peers": list(peers)}


@app.route('/mine', methods=['GET'])
def mineUnconfirmedTransactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        chainLength = len(blockchain.chain)
        consensus()
        if chainLength == len(blockchain.chain):
            announceNewBlock(blockchain.lastBlock)
        return "Block #{} is mined.".format(blockchain.lastBlock.index)


@app.route('/count', methods=['GET'])
def getPeerCount():
    print(peers)
    print(len(peers))
    return "Done"


def createChainFromDump(chainDump):
    generatedBlockchain = Blockchain()
    generatedBlockchain.createGenesisBlock()
    for idx, blockData in enumerate(chainDump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(blockData["index"],
                      blockData["transactionType"],
                      Product(blockData["product"]["productId"], blockData["product"]["productType"], blockData["product"]["isCertified"]),
                      blockData["timestamp"],
                      blockData["previous_hash"],
                      OwnerRelation(blockData["ownerRelation"]["ownerKey"], blockData["ownerRelation"]["name"], blockData["ownerRelation"]["relType"]),
                      Location(blockData["location"]["lat"], blockData["location"]["lng"]),
                      blockData["nonce"])
        proof = blockData['hash']
        added = generatedBlockchain.addBlock(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generatedBlockchain


@app.route('/pending_tx')
def getPendingTx():
    return json.dumps(blockchain.unconfirmedTransactions)


def consensus():
    global blockchain

    longestChain = None
    currentLen = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > currentLen and blockchain.checkChainValidity(chain):
            currentLen = length
            longestChain = chain

    if longestChain:
        blockchain = longestChain
        return True
    return False


def announceNewBlock(block):
    for peer in peers:
        url = "{}addBlock".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data={'block': json.dumps(block.__dict__, sort_keys=True), 'prodId': blockchain.prodId},
                      headers=headers)

def hashPassword(password):
    return sha256(password.encode()).hexdigest()


def timeStampToString():
    return datetime.datetime.utcnow().strftime("%a %b %d %Y %I:%M:%S %p")

#app.run(debug=True, port=8000)