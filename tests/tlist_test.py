# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import unittest
from polymorph.utils import readpcap


class TListTestCase(unittest.TestCase):
    def setUp(self):
        self.tlist = readpcap('tests/test.pcap')

    def test_size(self):
        self.assertEqual(len(self.tlist), 732)

    def test_getitem_fromlist(self):
        item = self.tlist[3]
        self.tlist[400]
        self.assertEqual(item, self.tlist[3])
        with self.assertRaises(IndexError):
            self.tlist[900]

    def test_getitem_after_write(self):
        item = self.tlist[20]
        self.tlist.write(path='/dev/null')
        self.assertEqual(item, self.tlist[20])

    def test_generate_templates(self):
        item = self.tlist[3]
        self.tlist[10]
        self.tlist._generate_templates()
        self.assertEqual(item, self.tlist[3])

    def test_repr(self):
        self.assertEqual(self.tlist.__repr__(),
                         "<tlist.TemplatesList: 732 templates>")
