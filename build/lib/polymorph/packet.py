# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from collections import OrderedDict
from polymorph.converter import Converter

raw = None


class Packet(object):
    """This class encapsulates the packets intercepted by nfqueue in such
    a way that they are easily accessible by the users."""

    def __init__(self, template):
        """Initialization method of the `Packet` class.

        Parameters
        ----------
        template : :obj:`Template`
            A `Template` object that will be parsed to obtain the fields and
            layers.

        """
        self._layers = {l.name: PacketLayer(l)
                        for l in template.layers}
        self.drop = False
        self.rec_chksums = True

    def __getitem__(self, item):
        return self._layers[item]

    def __len__(self):
        return len(self.raw)

    @property
    def raw(self):
        """:obj:`bytes`: Packet bytes."""
        global raw
        # The payload is returned without the Ethernet layer
        return raw[14:]

    @raw.setter
    def raw(self, value):
        global raw
        # Padding for Ether layer that nfqueue.get_payload() ignores
        # TODO: Do this in a better way
        raw = b'\x00' * 14 + value

    def get_payload(self):
        """Returns the payload of the packet in bytes."""
        return self.raw

    def set_payload(self, payload):
        """Sets the payload of the packet.

        Parameters
        ----------
        payload : :obj:`bytes`
            The packet in bytes without the ethernet layer.

        """
        self.raw = payload

    def global_var(self, name, default):
        """Creates a global variable.

        Parameters
        ----------
        name: :obj:`str`
            The name of the global variable.
        default: :obj
            The default value of the global variable.

        """
        try:
            eval("self." + str(name))
        except AttributeError:
            setattr(self, name, default)

    def insert(self, index1, index2, value):
        """Inserts a value between two index in the payload.

        Parameters
        ----------
        index1: int
            First index in the payload.
        index2: int
            Second index in the payload.
        value: :obj:`bytes`
            Value to insert in the payload.

        """
        if index1 >= index2 and type(value) is not bytes:
            raise ValueError
        else:
            payload = b'\x00' * 14 + self.raw
            payload = payload[:index1] + value + payload[index2:]
            self.raw = payload[14:]


class PacketLayer(object):
    """This class encapsulates de Template layers, so the user can access the
    content of the intercepted packet in an easy an intuitive way."""

    def __init__(self, tlayer):
        """Initialization method of the class.

        Parameters
        ----------
        tlayer : :obj:`TLayer`
ampl            A template layer for accessing the raw intercepted packet.

        """
        self._tlayer = tlayer
        self._struct = tlayer.get_structs()
        self._fields = {f.name: (f.slice, f.type, f.mask, f.size)
                        for f in tlayer.fields}
        self._cv = Converter()

    def __getitem__(self, item):
        global raw
        fslice, ftype, fmask, fsize = self._fields[item]
        if item in self._struct:
            fstruct = self._struct[item]
            fraw = fstruct.parse(raw)[item]
        else:
            fraw = raw[fslice]
        # Return the field with the appropriate interpretation
        return self._cv.get_frepr(ftype, fraw, fsize, fmask, item)

    def __setitem__(self, key, value):
        global raw
        fslice, ftype, fmask, fsize = self._fields[key]
        if key in self._struct:
            fstruct = self._struct[key]
            fraw = fstruct.parse(raw)
            start_byte = PacketLayer._get_start_byte(fstruct, fraw, key)
            fsize = len(fraw[key])
            stop_byte = start_byte + fsize
        else:
            start_byte = fslice.start
            stop_byte = fslice.stop
            fraw = raw[fslice]
        # obtain the bytes from the representation of the field
        fraw = self._cv.get_fraw(value, ftype, fraw, fsize, fmask, key)
        # add the new value to the packet content
        raw = raw[:start_byte] + fraw + raw[stop_byte:]

    def __len__(self):
        global raw
        return len(raw) - self._tlayer.slice.start

    @staticmethod
    def _getflens(st, praw):
        d = OrderedDict()
        for s in st.subcons:
            try:
                d[s.name] = s.sizeof()
            except:
                d[s.name] = None
        for f in praw:
            try:
                if not d[f]:
                    d[f] = len(praw[f])
            except KeyError:
                pass
        return d

    @staticmethod
    def _get_start_byte(fstruct, fraw, field):
        flens = PacketLayer._getflens(fstruct, fraw)
        st_byte = 0
        for f in flens:
            if f == field:
                break
            st_byte += flens[f]
        return st_byte

    @property
    def slice(self):
        return self._tlayer.slice
