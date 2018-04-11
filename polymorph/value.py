# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

class Value:
    """This class represents the value of a field in the template"""

    def __init__(self, bytesvalue, ftype=None):
        """Initialization method for the Value class.

        Parameters
        ----------
        bytesvalue : :obj:`bytes`
            The value of the field encoded in bytes.

        """
        self._rawvalue = bytesvalue
        self._type = ftype
        self._value = self._guess_repr()

    def __bytes__(self):
        value = bytes(self._rawvalue)
        self._type = (bytes, None)
        return value

    def __repr__(self):
        return str(self._value)

    def hex(self):
        value = self._rawvalue.hex()
        self._type = (str, 'hex')
        return value

    @property
    def value(self):
        return self._value

    def _guess_repr(self):
        if self._type:
            try:
                if self._type[0] is int:
                    return int.from_bytes(self._rawvalue, self._type[1])
                elif self._type[0] is str:
                    if self._type[1] == 'hex':
                        return self._rawvalue.hex()
                    return self._rawvalue.decode()
                elif self._type[0] is bytes:
                    return self._rawvalue
            except UnicodeError:
                self._type = (str, 'hex')
                return self._rawvalue.hex()
        else:
            try:
                self._type = (str, None)
                return self._rawvalue.decode()
            except UnicodeDecodeError:
                self._type = (int, 'big')
                return int.from_bytes(self._rawvalue, byteorder='big')

    def to_int(self, order='big'):
        self._value = int.from_bytes(self._rawvalue, byteorder=order)
        self._type = (int, order)

    def to_str(self):
        self._value = self._rawvalue.decode()
        self._type = (str, None)

    def to_hex(self):
        self._value = self.hex()
        self._type = (str, 'hex')

    def to_bytes(self):
        self._value = self._rawvalue
        self._type = (bytes, None)

    def type(self):
        return self._type
