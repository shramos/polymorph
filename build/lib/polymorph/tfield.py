# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from collections import OrderedDict
from termcolor import colored
from polymorph.ftype import Ttype, Ftype
from polymorph.converter import Converter


class TField(object):
    """This class represents a field in a `Template`."""

    def __init__(self, fname, fslice, fsize, pkt_raw, trepr,
                 ttype, tmask, layer, ftype=None, frepr=None):
        """Initialization method for the `TField` class.

        Parameters
        ----------
        fname : :obj:`str`
            The name of the `TField`.
        fslice : :obj:`slice`
            :obj:`slice` representing the position of the `TField` 
            in the raw packet data.
        fsize : int
            Size of the `TField` in bytes.
        pkt_raw : :obj:`bytes`
            Packet content in bytes.
        trepr : :obj:`str`
            Custom representation of `TField` according to Tshark.
        ttype : :obj:`str`
            Type of the `TField` according to Tshark.
        tmask : int
            Mask for calculate binary fields
        layer : :obj:`TLayer`
            Parent layer.
        ftype : :obj:`Frype`, optional
            Type of the field.
        frepr : :obj:`obj`, optional
            Representation of the field according to its type.

        """
        self._fname = fname.lower()
        self._fslice = fslice
        self._pkt_raw = pkt_raw
        self._fraw = pkt_raw[fslice]
        self._ttype = ttype
        self._trepr = trepr
        self._fsize = fsize
        self._layer = layer
        self._fmask = tmask
        self._frepr = frepr
        self._ftype = ftype
        # If you have the ftype but not the frepr
        if ftype and not frepr:
            cv = Converter()
            self._frepr = cv.get_frepr(ftype, self._fraw, fsize, tmask, fname)
        # If you not have the ftype
        elif not ftype:
            try:
                self._get_ftype_frepr(ttype, self._fraw, fsize, tmask, trepr)
            # In case of failure, ftype FT_HEX
            except:
                cv = Converter()
                self._ftype = Ftype.FT_HEX
                self._frepr = cv.raw2hex(self._fraw)

    def __repr__(self):
        return "<tfield.TField: %s>" % self._fname

    def __len__(self):
        return self._fsize

    def is_int(self):
        """Check if the `TField` is of type `int` or `long`.

        Returns
        -------
        bool
            True if it is of type `int` or `long`, False otherwise.

        """
        return self._ftype in [Ftype.FT_INT_BE, Ftype.FT_INT_LE]

    def is_str(self):
        """Check if the `TField` is of type `str`.

        Returns
        -------
        bool
            True if it is of type `str`, False otherwise.

        """
        return self._ftype in [Ftype.FT_STRING]

    def is_hex(self):
        """Returns true if value is hex.

        Parameters
        ----------
        value: :obj:`str`
            A string that can be or not hex.

        """
        return self._ftype in [Ftype.FT_HEX]

    @property
    def name(self):
        """str: Name of the `TField` in `str` and lowercase."""
        return self._fname

    @name.setter
    def name(self, value):
        self._fname = value.lower()

    @property
    def pkt_raw(self):
        """bytes: Bytes of the packet."""
        return self._pkt_raw

    @property
    def value(self):
        return self._frepr

    @property
    def raw(self):
        return self._fraw

    @property
    def slice(self):
        return self._fslice

    def hex(self):
        """str: Returns the value encoded in hexadecimal of the `TField`.

        """
        return self._fraw.hex()

    @property
    def size(self):
        """int: Returns the size of the `TField`."""
        return self._fsize

    @property
    def mask(self):
        """int: Returns the mask of the `TField`."""
        return self._fmask

    @property
    def type(self):
        """:obj:`tuple`: Returns the type of the `TField`."""
        return self._ftype

    @property
    def layer(self):
        """str: Returns the name of the parent `TLayer`."""
        return self._layer

    @layer.setter
    def layer(self, value):
        self._layer = value

    def show(self):
        """Show a the properties of the `TField`."""
        print('\n', colored("---[ %s ]---" %
                            self._fname, 'white', attrs=['bold']), sep="")
        print('{0: <20}'.format("value"), "=", colored(self._frepr, 'cyan'))
        print('{0: <20}'.format("type"), "=",
              colored(str(self._ftype)[6:], 'cyan'))
        print('{0: <20}'.format("bytes"), "=", colored(self._fraw, 'cyan'))
        print('{0: <20}'.format("hex"), "=", colored(self.hex(), 'cyan'))
        print('{0: <20}'.format("size"), "=",
              colored(str(self._fsize), 'cyan'))
        print('{0: <20}'.format("slice"), "=",
              colored(str(self._fslice), 'cyan'))
        print('{0: <20}'.format("mask"), "=",
              colored(str(self._fmask), 'cyan'), "\n")

    def dict(self):
        """Build a dictionary with all the elements of the `TField`.

        Returns
        -------
        :obj:`dict`
            Dictionary with all the attributes of the `TField`.

        """
        return OrderedDict([("name", self._fname),
                            ("value", self._fraw.hex()),
                            ("type", self._ftype.value),
                            ("size", self._fsize),
                            ("slice", str(self._fslice)),
                            ("frepr", self._frepr if self._ftype !=
                             Ftype.FT_BYTES else self._frepr.hex()),
                            ("mask", self._fmask),
                            ("ttype", self._ttype),
                            ("trepr", self._trepr)])

    def _get_ftype_frepr(self, ttype, fraw, fsize, fmask, trepr):
        """Extract the field type and representation from the Tshark
        type and the raw value."""
        # Initialization of a type-converting object
        cv = Converter()
        #
        # Tshark INT type evaluation
        #
        if Ttype(ttype) in [Ttype.FT_UINT8, Ttype.FT_UINT16, Ttype.FT_UINT24,
                            Ttype.FT_UINT32, Ttype.FT_UINT40, Ttype.FT_UINT48,
                            Ttype.FT_UINT56, Ttype.FT_UINT64, Ttype.FT_INT8,
                            Ttype.FT_INT16, Ttype.FT_INT24, Ttype.FT_INT32,
                            Ttype.FT_INT40, Ttype.FT_INT48, Ttype.FT_INT56,
                            Ttype.FT_INT64, Ttype.FT_IEEE_11073_SFLOAT,
                            Ttype.FT_IEEE_11073_FLOAT, Ttype.FT_FLOAT,
                            Ttype.FT_DOUBLE, Ttype.FT_BOOLEAN]:
            if fmask != 0:
                self._ftype = Ftype.FT_BIN_BE
                self._frepr = cv.raw2bin(fraw, fmask, fsize)
            elif trepr[:2] == "0x":
                self._ftype = Ftype.FT_HEX
                self._frepr = cv.raw2hex(fraw)
            else:
                ft_int_be = int.from_bytes(fraw, byteorder='big')
                ft_int_le = int.from_bytes(fraw, byteorder='little')
                if ft_int_be == int(trepr):
                    self._ftype = Ftype.FT_INT_BE
                    self._frepr = ft_int_be
                elif ft_int_le == int(trepr):
                    self._ftype = Ftype.FT_INT_LE
                    self._frepr = ft_int_le
                else:
                    prev_fields = self._layer.fields
                    if len(prev_fields) > 0 and prev_fields[-1].slice == self._fslice:
                        self._ftype = Ftype.FT_BIN_BE
                        self._frepr, self._fmask = cv.raw2maskbin(
                            fraw, prev_fields[-1].mask, fsize)
                    else:
                        self._ftype = Ftype.FT_HEX
                        self._frepr = cv.raw2hex(fraw)
        #
        # Tshark String and Char type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_CHAR, Ttype.FT_STRING, Ttype.FT_STRINGZ,
                              Ttype.FT_UINT_STRING]:
            self._ftype = Ftype.FT_STRING
            self._frepr = cv.raw2string(fraw)
        #
        # Tshark Bytes type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_BYTES, Ttype.FT_UINT_BYTES, Ttype.FT_VINES]:
            self._ftype = Ftype.FT_BYTES
            self._frepr = fraw
        #
        # Tshark Hex type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_IPXNET, Ttype.FT_PCRE, Ttype.FT_GUID,
                              Ttype.FT_OID, Ttype.FT_AX25, Ttype.FT_REL_OID,
                              Ttype.FT_SYSTEM_ID, Ttype.FT_STRINGZPAD,
                              Ttype.FT_FCWWN, Ttype.FT_NUM_TYPES, Ttype.FT_FRAMENUM,
                              Ttype.FT_HEX, Ttype.FT_PROTOCOL]:
            self._ftype = Ftype.FT_HEX
            self._frepr = cv.raw2hex(fraw)
        #
        # Tshark Absolute Time type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_ABSOLUTE_TIME]:
            self._ftype = Ftype.FT_ABSOLUTE_TIME
            self._frepr = cv.raw2absolute(fraw, fsize, self._fname)
            # If the date interpretation is wrong
            if self._frepr[:20] != self._trepr[:20] or not self._frepr:
                self._ftype = Ftype.FT_HEX
                self._frepr = cv.raw2hex(fraw)
        #
        # Tshark Relative Time type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_RELATIVE_TIME]:
            self._ftype = Ftype.FT_RELATIVE_TIME
            self._frepr = cv.raw2relative(fraw)
        #
        # Tshark Ether type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_ETHER]:
            self._ftype = Ftype.FT_ETHER
            self._frepr = cv.raw2ether(fraw)
        #
        # Tshark ipv4 type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_IPv4]:
            self._ftype = Ftype.FT_IPv4
            self._frepr = cv.raw2ipv4(fraw)
            if not self._frepr:
                self._ftype = Ftype.FT_HEX
                self._frepr = cv.raw2hex(fraw)
        #
        # Tshark ipv6 type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_IPv6]:
            self._ftype = Ftype.FT_IPv6
            self._frepr = cv.raw2ipv6(fraw)
            if not self._frepr:
                self._ftype = Ftype.FT_HEX
                self._frepr = cv.raw2hex(fraw)
        #
        # Tshark Eui64 type evaluation
        #
        elif Ttype(ttype) in [Ttype.FT_EUI64]:
            self._ftype = Ftype.FT_EUI64
            self._frepr = cv.raw2eui64(fraw)
        #
        # Tshark type not specified
        #
        else:
            self._ftype = Ftype.FT_HEX
            self._frepr = cv.raw2hex(fraw)
