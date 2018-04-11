# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import unittest
from polymorph.tgenerator import TGenerator
from scapy.all import Ether, IP

pkt = """\
0800271684730015c7b2700008004500007975e100003d11918e0a5f79bd0a5fe7890035d3750\
06507cf8d0781800001000000010000037777770a6578706c6f69742d646203636f6d00001c00\
01c0100006000100000708002d036e7332056e6f2d6970c01b0a686f73746d6173746572c0347\
7c09d9a00002a300000070800093a8000000708"""


class TGeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.tgen = TGenerator('tests/test.pcap')

    def test_dissect_fields(self):
        scapy_pkt = Ether(bytearray.fromhex(pkt))
        offset = len(scapy_pkt[Ether]) - len(scapy_pkt[IP])
        diss_fields = self.tgen._dissect_fields(scapy_pkt[IP], offset)
        length = eval(diss_fields['len'])
        chksum = eval(diss_fields['chksum'])
        dst = eval(diss_fields['dst'])
        self.assertEqual(length, slice(16, 18))
        self.assertEqual(chksum, slice(24, 26))
        self.assertEqual(dst, slice(30, 34))
