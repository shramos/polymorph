# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from collections import OrderedDict
from random import randint
from polymorph.tfield import TField
from termcolor import colored
from construct import *


class TLayer(object):
    """Class that represents a layer within a `Template`."""

    def __init__(self, name, lslice, raw, fields=None, custom=False):
        """Initialization method of the class.

        Parameters
        ----------
        name : str
            Name of the layer.
        lslice : :obj:`str`
            :obj:`slice` encoded in hexadecimal representing the position
            of the `TLayer` in the raw packet data.
        raw : :obj:`str`
            Package content bytes encoded in hexadecimal.
        fields : :obj:`OrderedDict`, optional
            Dictionary with the fields of the layer of the form
            {fieldname : `TField`}.
        custom : bool, optional
            False if the layer has not been modified by the user or the tool
            True if the layer has been modified/built by the user or the tool.

        """
        if not fields:
            fields = OrderedDict()
        self._fields = fields
        self._name = name.upper()
        self._custom = custom
        self._raw = raw
        self._lslice = lslice
        self._structs = OrderedDict()
        self._save_structs = OrderedDict()
        # This constants will help constructing the structs
        self._nums = {'1': {'big': Int8ub,
                            'little': Int8ul},
                      '2': {'big': Int16ub,
                            'little': Int16ul},
                      '3': {'big': Int24ub,
                            'little': Int24ul},
                      '4': {'big': Int32ub,
                            'little': Int32ul}}

    def __repr__(self):
        return "<tlayer.TLayer(%s): %s>" % (self._name, " ".join([f.name for f in self._fields.values()]))

    def __getitem__(self, field):
        return self.getfield(field)

    def is_custom(self):
        """Returns True if the `TLayer` has been set as custom,
        False otherwise.

        Returns
        -------
        :obj:`bool`

        """
        return self._custom

    def set_custom(self):
        """Sets the :obj:`TLayer` as custom."""
        self._custom = True

    @property
    def name(self):
        """str: Name of the `TLayer`."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.upper()

    @property
    def slice(self):
        """:obj:`slice`: Slice that represents the position of the `TLayer`
        in the raw payload.

        The setter will encode de slice object into hexadecimal to be stored.
        """
        return eval(bytearray.fromhex(self._lslice))

    @slice.setter
    def slice(self, value):
        if type(value) is not slice:
            raise TypeError
        self._lslice = str(value).encode().hex()

    @property
    def raw(self):
        """:obj:`bytearray` : Package content in raw (bytes representation)."""
        return bytearray.fromhex(self._raw)

    @property
    def fields(self):
        """:obj:`list` of :obj:`TField`: Obtain all the fields of the
        `TLayer`."""
        return self.getfields()

    def add_struct(self, fname, fdeps, start_byte, expression):
        """This function creates a structure that relates a field to other
        fields of the layer, so that its value can be calculated dynamically
        at run time. Perform additional processing before sending the data
        to create_struct.

        Parameters
        ----------
        fname: :obj:`str`
            Name of the field which value will be recalculated.
        fdeps: :obj:`list` of :obj:`str`
            Dependen fields.
        start_byte: :obj:`str`
            Byte in which the value of the main field begins. Must be a `str`.
            Fields must be preceded by 'this'. It can be a complex expression:
            '70 - this.field_len'
        expression: :obj:`str`
            Expression with which the new field value will be calculated
            dynamically. Fields must be preceded by 'this'. Can be complex:
            'this.field_len - this.field2_len - 2'

        """
        # This is used for saving the structs to the template
        self._save_structs[fname] = {"fdeps": fdeps,
                                     "sb": start_byte,
                                     "exp": expression}
        # Extract fields
        dep_fields = [self.getfield(f) for f in fdeps]
        main_field = self.getfield(fname)
        # Processing the start_byte expression
        st = self.create_struct(main_field, dep_fields, start_byte, expression)
        self._structs[fname] = st

    def test_struct(self, tfieldname):
        """Tests de result of the Struct for a particula `TField`.

        Parameters
        ----------
        tfieldname: :obj:`str`
            Name of the `TField` to be deleted.

        """
        if tfieldname in self._structs:
            return self._structs[tfieldname].parse(self.raw).__getitem__(tfieldname)

    def del_struct(self, tfieldname):
        """Deletes a `Struct` from a `TField`/

        Parameters
        ----------
        tfieldname: :obj:`str`
            Name of the `TField` to be deleted.

        """
        if tfieldname in self._structs:
            del self._structs[tfieldname]

    def get_struct(self, tfieldname):
        """Returns the `Struct` for a particula `TField`.

        Parameters
        ----------
        tfieldname: :obj:`str`
            Name of the `TField`.

        Returns
        -------
        :obj:`Struct`

        """
        if tfieldname in self._structs:
            return self._structs[tfieldname]

    def show_structs(self, tfname):
        """Pretty Print of the Structs of a `TField`.

        Parameters
        ----------
        tfname: :obj:`str`
            Name of the `TField`.

        """
        if tfname not in self._structs:
            return
        print(colored('\n--- Structs for %s ---' % tfname,
                      'cyan', attrs=['bold']))
        for s in self._structs[tfname].subcons:
            if s.name[-3:] != "pad":
                print(colored(s.name, 'cyan'))
            else:
                print(s.name)
            print('-' * 10)
        print()

    def get_structs(self):
        """Returns the `Struct` for all the `Tfields` in the `TLayer`.

        Returns
        -------
        :obj:`OrderedDict`

        """
        return self._structs

    def is_struct(self, tfieldname):
        """Returns True if the `TField` has a particular `Struct` associated.

        Parameters
        ----------
        tfieldname : :obj:`str`
            Name of the `TField`.

        Returns
        -------
        :obj:`bool`
            True if the `TField` has a `Struct` object associated,
            False otherwise.

        """
        return tfieldname in self._structs

    def create_struct(self, tfield, fdeps, start_byte, expression):
        """This function creates a structure that relates a field to other
         fields of the layer, so that its value can be calculated dynamically
          at run time.

        Parameters
        ----------
        tfield : :obj:`TField`
            Field for which the new value will be calculated.
        fdeps: :obj:`list` of :obj:`TField`
            List of fields on which the previous field depends.
        start_byte: :obj:`str`
            Byte in which the value of the main field begins. Must be a `str`.
            Fields must be preceded by 'this'. It can be a complex expression:
            '70 - this.field_len'
        expression: :obj:`str`
            Expression with which the new field value will be calculated
            dynamically. Fields must be preceded by 'this'. Can be complex:
            'this.field_len - this.field2_len - 2'

        Returns
        -------
        :obj:`Struct`
            Structure that allows to parse the raw bytes of the packet and
             return the exact value of the field.

        """
        # Ordering the dependencies
        ordered_list = sorted(fdeps, key=lambda f: f.slice.start)
        # Building the Struct dependencies
        st = Struct()
        stop_byte = 0
        for field in ordered_list:
            st_byte = field.slice.start - stop_byte
            stop_byte = field.slice.stop
            # Adding padding to the Struct
            fname = field.name + "pad"
            st += fname / Bytes(st_byte)
            # Adding the field
            st += field.name / self._nums[str(field.size)][field.order()]
        # Building the struct main field
        # Adding paddig to the struct
        fname = tfield.name + "pad"
        st += fname / Bytes(eval(start_byte) - stop_byte)
        # Adding the field
        st += tfield.name / Bytes(eval(expression))
        return st

    def customfields(self):
        """Obtain all the `Tfield` in the template that have been modified

        Returns
        -------
        :obj:`list` of :obj:`Tfield`
            List of fields that have the custom attribute set to True.

        """
        return [f for f in self.getfields() if f.is_custom()]

    def addfield(self, field):
        """Adds a `TField` to the actual `TLayer`.

        Note
        ----
        If a `TField` with the same name is alreadry in the `TLayer`,
        we append a random 3 digit number to the name.

        Parameters
        ----------
        field : :obj:`TField`
            Field that will be added to the `TLayer`.

        """
        fname = field.name
        if fname not in self._fields:
            self._fields[fname] = field
        else:
            # TODO: change this solution
            rand = str(randint(0, 999))
            field.name = fname + rand
            self._fields[fname + rand] = field

    def delfield(self, field):
        """Deletes a `TField` from the `TLayer`.

        Parameters
        ----------
        field : :obj:`TField`, str
            Field that will be deleted from the `TLayer`.

        """
        if type(field) is TField:
            self._fields.pop(field.name)
        elif type(field) is str:
            self._fields.pop(field.lower())

    def getfield(self, fieldname):
        """Obtain a `TField` from the `TLayer`.

        Parameters
        ----------
        fieldname : str
            String with the name of a `TField`.

        Returns
        -------
        :obj:`TField`
            The object that has the name specified.
        :obj:`None`
            if there is no field with the specified name

        """
        if self.isfield(fieldname):
            return self._fields[fieldname.lower()]
        else:
            return None

    def getfields(self):
        """Get all the `TFields` in the `TLayer`.

        Returns
        -------
        :obj:`list` of :obj:`TFields`
            List of all `TField` in the `TLayer`.

        """
        return list(self._fields.values())

    def isfield(self, fieldname):
        """Check if there is a `TField` with that name in the `TLayer`.

        Parameters
        ----------
        fieldname : str
            Name of the field.

        Returns
        -------
        bool
            True if exists, False if not.

        """
        return fieldname.lower() in self._fields

    def fieldnames(self):
        """Returns the names of the `TField` of which the `TLayer` is formed.

        Returns
        -------
        :obj:`list` of :obj:`str`
            List with the names of the `TField` in `str`

        """
        return [f.name for f in self.getfields()]

    def show(self):
        """Pretty print of the `TLayer` object with types."""
        print('\n', colored("---[ %s ]---" % self._name, 'white', attrs=['bold']), sep="")
        for field in self.fields:
            ftype = 'uknown'
            if field.type[0] is int:
                ftype = 'int'
            elif field.type[0] is str:
                if field.type[1] == 'hex':
                    ftype = 'hex'
                else:
                    ftype = 'str'
            elif field.type[0] is bytes:
                ftype = 'bytes'
            print('{0: <35}'.format(colored(ftype, 'cyan', attrs=['bold']) + " " + field.name) +
                  "= " + str(field.value) + colored(" (%s)" % field.frepr, 'cyan'))
        print()

    def dict(self):
        """Build a dictionary with all the elements of the `TLayer`.

        Returns
        -------
        :obj:`dict`
            Dictionary with all the fields and attributes of the `TLayer`.

        """
        return OrderedDict([
            ("name", self._name),
            ("custom", self._custom),
            ("lslice", self._lslice),
            ("fields", [f.dict() for f in self._fields.values()]),
            ("structs", self._save_structs)
        ])
