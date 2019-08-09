from flask import Flask, jsonify, abort, make_response, request, url_for
from flask import render_template, redirect
import json
import re
import requests
import hashlib
import os
from web3 import Web3

rpc = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(rpc))
contract_addr = '0x8fDd21C593c5693788E0248b4C86bB66375f8dA7'
abi = '[{"constant":true,"inputs":[],"name":"candidatesCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidates","outputs":[{"name":"id","type":"uint256"},{"name":"name","type":"string"},{"name":"voteCount","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"voters","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_candidateId","type":"uint256"}],"name":"votedEvent","type":"event"},{"constant":false,"inputs":[{"name":"_candidateId","type":"uint256"}],"name":"vote","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

app = Flask(__name__)

accounts = [ 
    '0xB0BE5EFDe83490f0d8fC64120461660098AE7599',
    '0xe0e577218063fc8648A4b04fDcFe2fD02990f734',
    '0xA55a74F93a50529f6F85658C22538eD9035551c3',
    '0x0b918ccbA35F62d80530F0223e0eA0DaB0C879BA',
    '0xCfc9EA020080496D2162B6EE8BFC84B5fbDF1FB5',
    '0xd84A6127e81Eb9384eB30b6A2D54E29A91798651',
    '0x35A3c8A48fb58B1d418D62c752Eeb4DA36128564',
    '0x50EC809051d823D0F979a1a974Ad63568bf7BEC1',
    '0x56Df378eF6AEB25Ec4fa22eDdB8f88B8407C2334',
    '0xa5cc1434694afA6daB030EEa5D6e4235e405643E' 
]

privatekeys = [
    '25d9479cd21fb800522f8e0c74513f0730f7afac9f3ac7a23d8ad69b7103be52',
    '01519292e7b9fb0d98149b7b202cbd2b99d92857804140fe927855cc26026a9d',
    '34f4f6e8a79cb192b957965b7764eb949f588027aee590557160bd2eca64123c',
    'cc85e4484592eadf0681fe9f2d6297c1cf4cb81321fe9454b43ad04bedcab87a',
    '4997b54bc7b835335f4324ef4e9f27fc78e42068799c07dba7f2ee517e995808',
    '448f522922fcfd184712c8b7e8bb82de255c6ca6aa8dda76d1e7aa4bdb819d49',
    '571f96e9291b198b7e024ab950d5868dbdc6b6137ee30bddb51ff450fa7591ce',
    '1e4acf03770503c9e5487fab22bb81484968a50b293d6bf528eb9e0fd5bd542e',
    '7c7aacbc4b3c839e0e870d6c08f63e3816c0b1384aa1dc6d05e9de95f2589106',
    '58f129cbace24078382559c366c6427f88179d35f2fac2ccdf62591e7e59cbac'
]

voted = []

@app.route("/" , methods=['POST'])
def home():
    data = eval(request.data) # {"aadhaarID":int(),"candidateID":int()}
    aid = data["aadhaarID"]-1
    if(aid in voted):
        return "Already voted",200
    try:
        cid = data["candidateID"]
        acc = accounts[aid]
        pvt = privatekeys[aid]
        contract = web3.eth.contract(address=contract_addr, abi=abi)
        transaction  = contract.functions.vote(cid).buildTransaction()
        transaction['nonce'] = web3.eth.getTransactionCount(acc)

        signed_tx = web3.eth.account.signTransaction(transaction, pvt)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        voted.append(aid)
        return str(web3.toHex(tx_hash)),200
    except:
        return "Error processing",500

@app.route("/results" , methods=['GET'])
def count():
    try:
        res = []
        election = web3.eth.contract(address=contract_addr, abi=abi)
        for i in range(election.call().candidatesCount()):    
            res.append(election.call().candidates(i+1))
        return json.dumps(res),200
    except:
        return "Error processing",500

if __name__ == '__main__':
	app.run(host="127.0.0.1" ,port=3000, debug = True)