# -*- coding: utf-8 -*-
import unittest
from genesis import get_genesis
import optparse

COIN = 100000000

class TestGenesis(unittest.TestCase):
    def test_sha256_bitcoin(self):
        options = OptionsHelper({
            'nonce': 2083236893,
            'algorithm': 'SHA256',
            'timestamp':
            'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
            'value': 50 * COIN,
            'time': 1231006505,
            'bits': 0x1d00ffff,
            'pubkey': '04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f'
        })
        merkle_hash, nonce, genesis_hash = get_genesis(options)
        self.assertEqual((merkle_hash, nonce, genesis_hash), ('4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b', '2083236893', '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'))

    def test_scrypt_litecoin(self):
        options = OptionsHelper({
            'nonce': 2084524493,
            'algorithm': 'scrypt',
            'timestamp':
            "NY Times 05/Oct/2011 Steve Jobs, Apple’s Visionary, Dies at 56",
            'value': 50 * COIN,
            'time': 1317972665,
            'bits': 0x1e0ffff0,
            'pubkey': '040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9'
        })
        merkle_hash, nonce, genesis_hash = get_genesis(options)
        self.assertEqual((merkle_hash, nonce, genesis_hash), ('97ddfbbae6be97fd6cdf3e7ca13232a3afff2353e29badfab7f73011edd4ced9', '2084524493', '12a765e31ffd4059bada1e25190f6e98c99d9714d334efa41a195a7e7e04bfe2'))

    def test_x11_dash(self):
        options = OptionsHelper({
            'nonce': 28917698,
            'algorithm': 'X11',
            'timestamp':
            "Wired 09/Jan/2014 The Grand Experiment Goes Live: Overstock.com Is Now Accepting Bitcoins",
            'value': 50 * COIN,
            'time': 1390095618,
            'bits': 0x1e0ffff0,
            'pubkey': '040184710fa689ad5023690c80f3a49c8f13f8d45b8c857fbcbc8bc4a8e4d3eb4b10f4d4604fa08dce601aaf0f470216fe1b51850b4acf21b179c45070ac7b03a9'
        })
        merkle_hash, nonce, genesis_hash = get_genesis(options)
        self.assertEqual((merkle_hash, nonce, genesis_hash), ('e0028eb9648db56b1ac77cf090b99048a8007e2bb64b68f092c03c7f56a662c7', '28917698', '00000ffd590b1485b3caadc19b22e6379c733355108f107a430458cdf3407ab6'))

    def test_quark_pivx(self):
        options = OptionsHelper({
            'nonce': 2402015,
            'algorithm': 'quark',
            'timestamp':
            'U.S. News & World Report Jan 28 2016 With His Absence, Trump Dominates Another Debate',
            'value': 250 * COIN,
            'time': 1454124731,
            'bits': 504365040,
            'pubkey': '04c10e83b2703ccf322f7dbd62dd5855ac7c10bd055814ce121ba32607d573b8810c02c0582aed05b4deb9c4b77b26d92428c61256cd42774babea0a073b2ed0c9'
        })
        merkle_hash, nonce, genesis_hash = get_genesis(options)
        self.assertEqual((merkle_hash, nonce, genesis_hash), ('1b2ef6e2f28be914103a277377ae7729dcd125dfeb8bf97bd5964ba72b6dc39b', '2402015', '0000041e482b9b9691d98eefb48473405c0b8ec31b76df3797c74a78680ef818'))

class OptionsHelper(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, attr, value):
        return self.update({attr: value})

if __name__ == '__main__':
    unittest.main()
