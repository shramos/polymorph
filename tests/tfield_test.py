# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import unittest
from scapy.all import Ether
from polymorph.utils import pkt_to_template

pkt = """\
00000000000000000000000086dd6000388e002c0640000000000000000000000000000000010\
0000000000000000000000000000001a648075be97ee5e6c973703b8018015600340000010108\
0af89d3535f89d3535300a000474657374686f6c61"""
repr = """\
<tlayer.TLayer(RAW.MQTT): hdrflags msgtype dupflag qos retain len topic_len \
topic msg>"""


class TFieldTestCase(unittest.TestCase):
    def setUp(self):
        self._template = pkt_to_template(Ether(bytearray.fromhex(pkt)))
        self._layer = self._template['RAW.MQTT']

    def test_repr(self):
        self.assertEqual(self._layer.__repr__(), repr)

    def test_to_int(self):
        self._layer['len'].to_int()
        self.assertEqual(type(self._layer['len'].value), int)

    def test_is_int(self):
        self._layer['len'].to_int()
        self.assertEqual(self._layer['len'].is_int(), True)

    def test_name(self):
        self.assertEqual(self._layer['topic_len'].name, 'topic_len')

    def test_value(self):
        self.assertEqual(self._layer['topic'].value, 'test')

    def test_valuehex(self):
        self.assertEqual(self._layer['topic'].valuehex, '74657374')

    def test_valuebytes(self):
        self.assertEqual(self._layer['topic'].valuebytes, b'test')

    def test_setvalue(self):
        self._layer['topic'].value = "new_topic"
        self.assertEqual(self._layer['topic'].value, 'new_topic')
        self._layer['topic'].value = b'topic'
        self.assertEqual(self._layer['topic'].value, b'topic')
        self._layer['topic'].value = "746f7069635f686578"
        self.assertEqual(self._layer['topic'].value, '746f7069635f686578')
        self._layer['topic'].value = 125
        self.assertEqual(self._layer['topic'].value, 125)

    def test_slice(self):
        self.assertEqual(type(self._layer['topic'].slice), slice)
