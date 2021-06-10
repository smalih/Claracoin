from datetime import datetime, time
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import json
import hashlib

class Blockchain():
    def __init__(self, difficulty=4, transactionLen=3):
        self.chain = [self.createGenesisBlock()]
        # diffculty determines how hard it is to mine a block
        self.difficulty = difficulty
        # transactionLen refers to how many pending transactions
        # there should be before they are mined as a block
        # ideally, I want the block to hold the transactions, so that
        # various blocks can be created and mined in parallel
        # but still added to the chain in sequence
        # Enhancement would be to add a timer as well
        # ie if ten transactions, or one hour has elapsed since creation of block
        # then mine the block
        self.transactionLen = transactionLen
        #self.maxTransactionTime = 10
        self.pendingTransactions = []
        self.nodes = []

    def createNode(self):
        newNode = Node(len(self.nodes)+1, self.genKeys())
        return newNode

    def genKeys(self):
        key = RSA.generate(2048)
        privKey = key.export_key()
        with  open('private.pem', 'wb') as file_out:
            file_out.write(privKey)
        pubKey = key.public_key().export_key()
        with open('receiver.pem', 'wb') as file_out:
            file_out.write(pubKey)
        return (pubKey, privKey)
    
    def createGenesisBlock(self):
        genBlock = Block()
        print("Genesis block created")
        return genBlock
    
    def addBlock(self):
        # way of obtaining prevHash will not work if multiple blocks are to be in existence?
        newBlock = Block(index=len(self.chain)-1, transactions=self.pendingTransactions, prevHash=self.getLatestBlock().hash)
        attempts = 0
        while newBlock.hash[:self.difficulty] != '0' * self.difficulty:
            newBlock.nonce+=1
            attempts+=1
            newBlock.hash = newBlock.calculateHash()
            #print(f"Attempt {attempts}")
        print(f"This took {attempts} attempts")
        self.chain.append(newBlock)
        print(f"Block {newBlock.index} has been added to the chain")

    def getLatestBlock(self):
        return self.chain[-1]

    def addTransaction(self, transaction):
        self.pendingTransactions.append(transaction)
        if len(self.pendingTransactions) >= self.transactionLen:
            self.addBlock()
            self.pendingTransactions = []


class Node():
    def __init__(self, nodeId, keyPair):
        self.pubKey = keyPair[0]
        self.privKey = keyPair[1]
        self.id = nodeId


class Block():
    def __init__(self, index=0, nonce=0, timestamp=datetime.now(), transactions=[], prevHash=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp.strftime("%H%M%S %m%d%Y ")
        self.prevHash = prevHash
        self.nonce = nonce
       #self.mined_by = 
        self.hash = self.calculateHash()

    def calculateHash(self):
        hashTransactionStr = ""
        for transaction in self.transactions:
            hashTransactionStr+=transaction.hash
        hashStr = f"{self.timestamp}{self.prevHash}{self.index}{self.nonce}{hashTransactionStr}"
        hashEncoded = json.dumps(hashStr, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def verifyBlockTransactions(self):
        for transaction in self.transactions:
            if not(transaction.verifyTransaction()):
                return False


class Transaction():
    def __init__(self, sender, receiver, amount, timestamp=datetime.now()):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp.strftime("%H%M%S %m%d%Y ")
        self.hash = self.calculateHash()
        self.signature = self.signTransaction()

    def signTransaction(self):
        signer = pkcs1_15.new(self.sender.privKey)
        return signer.sign(self.hash)
    
    def verifyTransaction(self):
        try:
            pkcs1_15.new(self.sender.pubKey).verify(self.hash, self.signature)
            return True
        except(ValueError, TypeError):
            print("Error - Signature invalid")
            return False

    def calculateHash(self):
        hashStr = f"{self.timestamp}{self.sender}{self.receiver}{self.amount}"
        hashEncoded = json.dumps(hashStr, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

Claracoin = Blockchain()