# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import json
from polymorph.tlayer import TLayer
from polymorph.tfield import TField
from collections import OrderedDict
from datetime import datetime
import dill
from dill.source import getsource
from termcolor import colored
from os.path import dirname
import polymorph.functions
from os import listdir
from os.path import isfile, join
from polymorph.ftype import Ftype
from texttable import Texttable


class Template:
    """Main class that represents a template"""

    def __init__(self, name=None, raw=None, from_path=None,
                 description="", version="0.1", layers=None):
        """Initialization method of the Template class.

        Parameters
        ----------
        name : :obj:`str`, optional
            Name with which the template will be identified.
        raw : :obj:`bytes`, optional
            Packet content int bytes.
        from_path : :obj:`str`, optional
            Path to a previously created and stored `Template`.
        description: :obj:`str`
            Template description.
        version: :obj:`str`
            Template version.
        layers: :obj:`OrderedDict`
            Dictionary with the layer of the `Template` of the form 
            {layername : `TLayer`}.


        """
        self._functions = OrderedDict()
        self._timestamp = str(datetime.now())
        self._version = version
        self._description = description
        self._name = name
        self._layers = layers if layers else OrderedDict()
        self._raw = raw
        if from_path:
            self.read(from_path)
        # Path to custom functions
        self._funcs_path = dirname(polymorph.functions.__file__)

    def __repr__(self):
        return "<template.Template: %s>" % "/".join(self.layernames())

    def __getitem__(self, layer):
        return self.getlayer(layer)

    def write(self, path=None):
        """Writes a `Template` to disk.

        Parameters
        ----------
        path : str, optional
            Path where the `Template` will be written, if None
            the `Template` will be written in templates folder.

        """
        if not path:
            path = "../templates/" + self._name.replace("/", "_") + ".json"
        with open(path, 'w') as outfile:
            json.dump(self.dict(), outfile, indent=4)

    @property
    def name(self):
        """str: Name with which the template will be identified."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        """str: Description of the :obj:`Template`."""
        return self._description

    @description.setter
    def description(self, value):
        if type(value) is str:
            self._description = value
        else:
            raise TypeError

    @property
    def version(self):
        """str: Version of the :obj:`Template`."""
        return self._version

    @version.setter
    def version(self, value):
        if type(value) is str:
            self._version = value
        else:
            raise TypeError

    @property
    def timestamp(self):
        """str: Creation timestamp of the :obj:`Template`."""
        return self._timestamp

    @property
    def layers(self):
        """:obj:`list` of :obj:`TLayer`: Layers of which the template
        is composed."""
        return self.getlayers()

    @property
    def raw(self):
        """:obj:`bytearray` : Packet content in raw (bytes representation)."""
        return self._raw

    def del_function(self, name):
        """Deletes a function.

        Parameters
        ----------
        name : :obj:`str`
            Name of the function.

        """
        del self._functions[name]

    def get_function_source(self, name):
        """Returns a function source code.

        Parameters
        ----------
        name : :obj:`str`
            Name of the function.

        Returns
        -------
        :obj: `str`
            Source code of the function.

        """
        path = "%s/%s.py" % (self._funcs_path, name)
        if isfile(path):
            return open(path).read()
        return "[!] File is not in disk"

    def function_names(self):
        """Returns a list with all the existing functions names.

        Returns
        -------
        :obj: `list` of :obj: `str`
            List with the function names.
        """
        return list(self._functions)

    def get_function(self, name):
        """Returns a function object.

        Parameters
        ----------
        name : :obj:`str`
            Name of the function.

        Returns
        -------
        :obj: `function`
            Function obtained.

        """
        f = bytearray.fromhex(self._functions[name])
        return dill.loads(f)

    def add_function(self, name, func):
        """Add a new function that will be executed when intercepting packets.

        Parameters
        ----------
        name : :obj:`str`
            Name to identify the function in the `Template`.
        func : :obj:`function`
            Pointer to a function.

        """
        fdump = dill.dumps(func)
        self._functions[name] = fdump.hex()

    def change_func_pos(self, element, index):
        """Changes the position of a particular function.

        Parameters
        ----------
        element: :obj:`str`
            Name of the function to change.
        index: int
            New index of the function.

        """

        def move_element(lista, name, index):
            e = lista.pop(lista.index(name))
            lista.insert(index, e)

        ordered_keys = list(self._functions.keys())
        move_element(ordered_keys, element, index)
        self._functions = OrderedDict(
            (k, self._functions[k]) for k in ordered_keys)

    def layernames(self):
        """Returns the names of the `TLayer` of which the `Template` is formed.

        Returns
        -------
        :obj:`list` of :obj:`str`
            List with the names of the `TLayer` in `str`

        """
        return list(self._layers)

    def addlayer(self, layer):
        """Adds a `TLayer` to the actual `Template`.

        Note
        ----
        If a `TLayer` with the same name is already in the `Template`,
        we append a random 3 digit number to the name.

        Parameters
        ----------
        layer : :obj:`Tlayer`
            Layer that will be added to the `Template`.

        """
        lname = layer.name
        if lname not in self._layers:
            self._layers[lname] = layer
        else:
            new_lname = self._new_lname(lname, self._layers)
            layer.name = new_lname
            self._layers[new_lname] = layer

    def _new_lname(self, lname, all_fields):
        """Generates new names for fields with duplicate name."""
        if lname in all_fields:
            if lname[-1].isnumeric():
                return self._new_lname(lname[:-1] + str(int(lname[-1]) + 1), all_fields)
            else:
                return self._new_lname(lname + str(2), all_fields)
        else:
            return lname

    def dellayer(self, layer):
        """Deletes a `TLayer` from the `Template`.

        Parameters
        ----------
        layer : :obj:`Tlayer`, str
            Layer that will be deleted from the `Template`.

        """
        if type(layer) is TLayer:
            self._layers.pop(layer.name)
        elif type(layer) is str:
            self._layers.pop(layer.upper())

    def getlayers(self):
        """Get all the `TLayer` in the `Template`.

        Returns
        -------
        :obj:`list` of :obj:`TLayer`
            List of all `TLayer` in the `Template`.

        """
        return list(self._layers.values())

    def getlayer(self, layername):
        """Obtain a `TLayer` from the `Template`.

        Parameters
        ----------
        layername : str
            String with the name of a `TLayer`.

        Returns
        -------
        :obj:`TLayer`
            The object that has the name spicified.
        :obj:`None`
            if there is no layer with the specified name

        """
        if self.islayer(layername):
            return self._layers[layername.upper()]
        else:
            return None

    def islayer(self, layername):
        """Check if there is a layer with that name in the Template.

        Parameters
        ----------
        layername : str
            Name of the layer.

        Returns
        -------
        bool
            True if exists, False if not.

        """
        return layername.upper() in self._layers

    def getfieldvalhex(self, fieldname, layername):
        """Gets the value in hexadecimal of a `TField` in a `TLayer`.

        Parameters
        ----------
        fieldname : str
            The name of the field.
        layername : str
            The name of the layer.

        Returns
        -------
        str
            The value of the field encoded in hexadecimal.

        """
        layer = self.getlayer(layername)
        return layer[fieldname].valuehex

    def show(self):
        """Pretty print of the `Template` with field types."""
        print()
        for layer in self.layers:
            print(colored("---[ %s ]---" %
                          layer.name, 'white', attrs=['bold']))
            for field in layer.fields:
                print('{0: <35}'.format(colored(str(field.type)[
                      6:] + " ", 'cyan', attrs=['bold']) + field.name) + "= " + colored(str(field.value), 'cyan'))
            print()

    def show_functions(self, name=None, verbose=False):
        """Pretty print of the custom functions of the `Template`.

        Parameters
        ----------
        name: :obj:`str`
            Name of a particular function.
        verbose: bool
            Indicate if the user want to print the source code of the
            functions

        """

        def get_source(n):
            return self.get_function_source(n)

        t = Texttable()
        rows = [["Order", "Functions"]]
        func_names = list(self._functions)
        if name and name in func_names and verbose:
            print(get_source(name))
        elif verbose:
            for idx, n in enumerate(func_names):
                rows.append([idx, get_source(n)])
            t.add_rows(rows)
            print(t.draw())
        else:
            for idx, func_name in enumerate(func_names):
                rows.append([idx, func_name])
            t.add_rows(rows)
            print(t.draw())
        print("")

    def show_all_funcs(self, verbose=False):
        """Pretty print of the functions that are on disk.

        Parameters
        ----------
        verbose: bool
            Indicate if the user want to print the source code of the
            functions.

        """
        func_names = [f[:-3]
                      for f in listdir(self._funcs_path)
                      if isfile(join(self._funcs_path, f))
                      and f != "__init__.py"
                      and f[-3:] == ".py"]
        if verbose:
            for n in func_names:
                print(colored(n, 'cyan'))
                print(self.get_function_source(n))
        else:
            print("\n".join(func_names))
        print("")

    def dict(self):
        """Build a dictionary with all the elements of the `Template`.

        Returns
        -------
        :obj:`dict`
            Dictionary with all the fields and layers of the template.

        """
        return OrderedDict([("Name", self._name),
                            ("Description", self._description),
                            ("Version", self._version),
                            ("Timestamp", self._timestamp),
                            ("Functions", self._functions),
                            ("layers", [l.dict()
                                        for l in self._layers.values()]),
                            ("raw", self._raw.hex())])

    def read(self, path):
        """Reads a `Template` from disk.

        Parameters
        ----------
        path: str
            Path from which the template will be read.

        """
        with open(path) as t:
            template = json.load(t)
        # Reading and loading the template
        self._name = template['Name']
        self._version = template['Version']
        self._timestamp = template['Timestamp']
        self._description = template['Description']
        self._raw = bytes.fromhex(template['raw'])
        self._functions = template['Functions']
        # Reading and loading the layers
        for layer in template['layers']:
            l = TLayer(layer['name'], pkt_raw=self._raw,
                       lslice=eval(layer['lslice']))
            # Reading the structs
            structs = layer["structs"]
            # Reading and loading the fields
            for field in layer['fields']:
                f = TField(fname=field['name'],
                           fslice=eval(field['slice']),
                           fsize=field['size'],
                           pkt_raw=self._raw,
                           trepr=field['trepr'],
                           ttype=field['ttype'],
                           tmask=field['mask'],
                           layer=l,
                           ftype=Ftype(field['type']),
                           frepr=field['frepr'] if Ftype(field['type']) !=
                           Ftype.FT_BYTES else bytes.fromhex(field['frepr']))
                l.addfield(f)
            # Initialization of the structs
            for f in structs:
                l.add_struct(f, structs[f]['fdeps'],
                             structs[f]['sb'], structs[f]['exp'])
            self.addlayer(l)
