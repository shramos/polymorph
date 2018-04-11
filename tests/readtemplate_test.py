# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import unittest
from polymorph.utils import readtemplate

pkt = """\
0800271684730015c7b270000800452002f6302500003206c20bd83ac98e0a5fe7890050ed603\
bdb9eb306d1be10801800af80ee00000101080a96ec32e43e61e0f6485454502f312e31203230\
30204f4b0d0a436f6e74656e742d547970653a206170706c69636174696f6e2f6f6373702d726\
573706f6e73650d0a446174653a205475652c203036204d617220323031382030393a35333a35\
3920474d540d0a43616368652d436f6e74726f6c3a207075626c69632c206d61782d6167653d3\
334353630300d0a5365727665723a206f6373705f726573706f6e6465720d0a436f6e74656e74\
2d4c656e6774683a203436330d0a582d5853532d50726f74656374696f6e3a20313b206d6f646\
53d626c6f636b0d0a582d4672616d652d4f7074696f6e733a2053414d454f524947494e0d0a0d\
0a308201cb0a0100a08201c4308201c006092b0601050507300101048201b1308201ad308196a\
216041477c2b8509a677676b12dc286d083a07ea67eba4b180f32303138303330363037353332\
345a306b30693041300906052b0e03021a05000414f6edb0636232819a35f68d75a09d024a11a\
a6cad041477c2b8509a677676b12dc286d083a07ea67eba4b02083b5c00bbe2fb5cb68000180f\
32303138303330363037353332345aa011180f32303138303331333037353332345a300d06092\
a864886f70d01010b05000382010100614e02608b7f8f1b601fae2b8916e0caeb050922864728\
c76f6f81e2acbd2e2d50fbb65c687d61b40ca56df982c109a690ac8c2e0586b6c4423abf4f748\
a03ea6808155e9a95fa6f2a6f2071f477578cd9079fc13f129d0ae25c7d4373374f518d12df36\
d14d04e805ff814a4b68b71cbd22cb1de8f6606306eb00500e47ee66dd41d60fbec6e32f48cc9\
c5f8e36167aac31f32333fa72f2ca700e77d2a072aaa4c96a3cc773235acd48de951e5868c21c\
3b7602d6ab23960b87efe0faab706675340894462e723d1e025023914dd9d9572762b86533397\
e3764edd6956c216fbdc257f8d2336a63ba657246de1cdb69d00582558b808a6a4ae3c030eb59\
5a28"""


class ReadTemplateTestCase(unittest.TestCase):
    def setUp(self):
        self.template = readtemplate('tests/template_test.json')

    def test_repr(self):
        self.assertEqual(self.template.__repr__(),
                         '<template.Template: ETHER/IP/TCP/RAW/RAW.HTTP/RAW.OCSP>')

    def test_name(self):
        self.assertEqual(self.template.name, 'Template:/Ether/IP/TCP/Raw')
        self.template.name = "Test_name"
        self.assertEqual(self.template.name, 'Test_name')

    def test_layernames(self):
        self.assertEqual(self.template.layernames(),
                         ['ETHER', 'IP', 'TCP', 'RAW', 'RAW.HTTP', 'RAW.OCSP'])

    def test_getlayers(self):
        from polymorph.tlayer import TLayer
        layers = self.template.getlayers()
        self.assertEqual(type(layers), list)
        self.assertEqual(len(layers), 6)
        self.assertEqual(type(layers[0]), TLayer)

    def test_getlayer(self):
        from polymorph.tlayer import TLayer
        self.assertEqual(type(self.template.getlayer("RAW.OCSP")), TLayer)
        self.assertEqual(self.template.getlayer("OTHER"), None)

    def test_raw(self):
        self.assertEqual(self.template.raw, bytearray.fromhex(pkt))

    def test_addlayer(self):
        from polymorph.tlayer import TLayer
        layer = TLayer("TEST", lslice="", raw="", custom=True)
        self.template.addlayer(layer)
        self.assertEqual(self.template.layernames(),
                         ['ETHER', 'IP', 'TCP', 'RAW', 'RAW.HTTP', 'RAW.OCSP', 'TEST'])
        self.assertEqual(type(self.template.getlayer('TEST')), TLayer)
        self.assertEqual(len(self.template.getlayers()), 7)

    def test_dellayer(self):
        self.template.dellayer('RAW.OCSP')
        layer = self.template.getlayer('RAW.HTTP')
        self.template.dellayer(layer)
        self.assertEqual(self.template.layernames(),
                         ['ETHER', 'IP', 'TCP', 'RAW'])
        self.assertEqual(self.template.getlayer('RAW.OCSP'), None)
        self.assertEqual(len(self.template.getlayers()), 4)

    def test_customlayer(self):
        from polymorph.tlayer import TLayer
        self.template.addlayer(TLayer("TEST", lslice="", raw="", custom=True))
        clayers = self.template.customlayers()
        self.assertEqual(len(clayers), 3)
        self.assertEqual(clayers[0].name, "RAW.HTTP")
        self.assertEqual(clayers[1].name, "RAW.OCSP")
        self.assertEqual(clayers[2].name, "TEST")

    def test_islayer(self):
        self.assertEqual(self.template.islayer('RAW.OCSP'), True)
        self.assertEqual(self.template.islayer('TEST'), False)

    def test_version(self):
        self.assertEqual(self.template.version, "0.1")

    def test_description(self):
        self.assertEqual(self.template.description, "")
