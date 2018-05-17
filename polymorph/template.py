# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import json
from polymorph.tlayer import TLayer
from polymorph.tfield import TField
from random import randint
from collections import OrderedDict
from datetime import datetime
import dill
from dill.source import getsource
from termcolor import colored
import os
from os.path import dirname
import polymorph.conditions
from os import listdir
from os.path import isfile, join


class Template:
    """Main class that represents a template"""

    def __init__(self, name=None, raw=None, from_path=None,
                 description="", version="0.1"):
        """Initialization method of the Template class.

        Parameters
        ----------
        name : :obj:`str`, optional
            Name with which the template will be identified.
        raw : :obj:`str`, optional
            Package content bytes encoded in hexadecimal.
        from_path : :obj:`str`, optional
            Path to a previously created and stored `Template`.

        """
        self._functions = OrderedDict([('preconditions', OrderedDict()),
                                       ('executions', OrderedDict()),
                                       ('postconditions', OrderedDict())])
        self._timestamp = str(datetime.now())
        self._version = version
        self._description = description
        self._name = name
        self._layers = OrderedDict()
        self._raw = raw
        if from_path:
            self.read(from_path)
        # Path to conditions (precs, execs, posts)
        self._conds_path = dirname(polymorph.conditions.__file__)

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
        """:obj:`bytearray` : Package content in raw (bytes representation)."""
        return bytearray.fromhex(self._raw)

    def get_precondition(self, name):
        """Obtain the precondition from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the precondition.

        Returns
        -------
        :obj: ``function`
            Precondition function.

        """
        return self.get_function('preconditions', name)

    def get_postcondition(self, name):
        """Obtain the postcondition from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the postcondition.

        Returns
        -------
        :obj: ``function`
            Postcondition function.

        """
        return self.get_function('postconditions', name)

    def get_execution(self, name):
        """Obtain the execution from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the execution.

        Returns
        -------
        :obj: ``function`
            Execution function.

        """
        return self.get_function('executions', name)

    def del_function(self, func, name):
        """Deletes a function (precondition, postcondition, execution)

        Parameters
        ----------
        func : :obj:`str`
            Name of the function group (preconditions, postconditions, executions)
        name : :obj:`str`
            Name of the function.

        """
        del self._functions[func][name]

    def del_precondition(self, name):
        """Deletes a precondition from the set.

        Parameters
        ----------
        name: :obj:`str`
            Name of the precondition.

        """
        self.del_function('preconditions', name)

    def del_postcondition(self, name):
        """Deletes a postcondition from the set.

        Parameters
        ----------
        name: :obj:`str`
            Name of the postcondition.

        """
        self.del_function('postconditions', name)

    def del_execution(self, name):
        """Deletes an execution from the set.

        Parameters
        ----------
        name: :obj:`str`
            Name of the execution.

        """
        self.del_function('executions', name)

    def get_function_source(self, func, name):
        """Returns a precondition/postcondition/execution source code.

        Parameters
        ----------
        func : :obj:`str`
            Name of the function group (precondition, postcondition, execution)
        name : :obj:`str`
            Name of the function.

        Returns
        -------
        :obj: `str`
            Source code of the function.

        """
        path = "%s/%s/%s.py" % (self._conds_path, func, name)
        if os.path.isfile(path):
            return open(path).read()
        return "[!] File is not in disk"

    def get_precondition_source(self, name):
        """Obtain the precondition source code from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the precondition.

        Returns
        -------
        :obj: `str`
            Precondition function source code.

        """
        return self.get_function_source('preconditions', name)

    def get_postcondition_source(self, name):
        """Obtain the postcondition source code from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the postcondition.

        Returns
        -------
        :obj: `str`
            Postcondition function source code.

        """
        return self.get_function_source('postconditions', name)

    def get_execution_source(self, name):
        """Obtain the execution source code from the name.

        Parameters
        ----------
        name : :obj:`str`
            Name of the execution.

        Returns
        -------
        :obj: `str`
            Execution function source code.

        """
        return self.get_function_source('executions', name)

    def precondition_names(self):
        """Returns a list with all the existing precondition names.

        Returns
        -------
        :obj: `list` of :obj: `str`
            List with the precondition names.

        """
        return list(self._functions['preconditions'])

    def postcondition_names(self):
        """Returns a list with all the existing postconditions names.

        Returns
        -------
        :obj: `list` of :obj: `str`
            List with the postconditions names.

        """
        return list(self._functions['postconditions'])

    def execution_names(self):
        """Returns a list with all the existing execution names.

        Returns
        -------
        :obj: `list` of :obj: `str`
            List with the execution names.
        """
        return list(self._functions['executions'])

    def get_function(self, func, name):
        """Returns a precondition/postcondition/execution object.

        Parameters
        ----------
        func : :obj:`str`
            Name of the function group (precondition, postcondition, execution)
        name : :obj:`str`
            Name of the function.

        Returns
        -------
        :obj: `function`
            Function obtained.

        """
        f = bytearray.fromhex(self._functions[func][name])
        return dill.loads(f)

    def add_function(self, cond, name, func):
        """Add a new function that will be executed as a when intercepting
         packets.

        Parameters
        ----------
        cond : :obj:`str`
            Name of the condition set (preconditions, postconditions,
            executions).
        name : :obj:`str`
            Name to identify the function in the `Template`.
        func : :obj:`function`
            Pointer to a function.

        """
        fdump = dill.dumps(func)
        self._functions[cond][name] = fdump.hex()

    def add_precondition(self, name, func):
        """Add a new function that will be executed as a precondition when
        intercepting packets.

        Parameters
        ----------
        name : :obj:`str`
            Name to identify the function in the `Template`.
        func : :obj:`function`
            Pointer to a function.

        """
        self.add_function('preconditions', name, func)

    def add_postcondition(self, name, func):
        """Add a new function that will be executed as a postcondition when
        intercepting packets.

        Parameters
        ----------
        name : :obj:`str`
            Name to identify the function in the `Template`.
        func : :obj:`function`
            Pointer to a function.

        """
        self.add_function('postconditions', name, func)

    def add_execution(self, name, func):
        """Add a new function that will be executed as a execution when
        intercepting packets.

        Parameters
        ----------
        name : :obj:`str`
            Name to identify the function in the `Template`.
        func : :obj:`function`
            Pointer to a function.

        """
        self.add_function('executions', name, func)

    def change_cond_pos(self, cond, element, index):
        """Changes the position of a precondition, postcondition or execution.

        Parameters
        ----------
        cond: :obj:`str`
            Name of the conditional function (precondition, postcondition, execution).
        element: :obj:`str`
            Name of the conditional function to change.
        index: int
            New index of the conditional function.

        """

        def move_element(lista, name, index):
            e = lista.pop(lista.index(name))
            lista.insert(index, e)

        ordered_keys = list(self._functions[cond].keys())
        move_element(ordered_keys, element, index)
        self._functions[cond] = OrderedDict((k, self._functions[cond][k]) for k in ordered_keys)

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
            # TODO: change this solution
            rand = str(randint(0, 999))
            layer.name = lname + rand
            self._layers[lname + rand] = layer

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

    def customlayers(self):
        """Obtain all the `TLayer` in the template that have been modified

        Returns
        -------
        :obj:`list` of :obj:`TLayer`
            List of layers that have the custom attribute set to True.

        """
        return [l for l in self.getlayers() if l.is_custom()]

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
            print(colored("---[ %s ]---" % layer.name, 'white', attrs=['bold']))
            for field in layer.fields:
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
                print('{0: <35}'.format(colored(ftype + " ", 'cyan', attrs=['bold']) + field.name) +
                      "= " + str(field.value) + colored(" (%s)" % field.frepr, 'cyan'))
            print()

    def show_conditions(self, cond, name=None, verbose=False):
        """Pretty print of the Preconditions, Postconditions and Executions
        of the `Template`.

        Parameters
        ----------
        cond: :obj:`str`
            Indicate if the user want to print Precondtions, Postconditions,
             or Executions.
        name: :obj:`str`
            Name of a particular condition.
        verbose: bool
            Indicate if the user want to print the source code of the
            conditions.

        """

        def print_source(cond, n):
            print(colored(n, 'cyan'))
            print(self.get_function_source(cond, n))
            
        cond_names = list(self._functions[cond])
        if name and name in cond_names and verbose:
            print_source(cond, name)
        elif verbose:
            for n in cond_names:
                print_source(cond, n)
        else:
            print("\n".join(cond_names))
        print("")

    def show_all_conds(self, cond, verbose=False):
        """Pretty print of the Preconditions, Postconditions and Executions
        that are on disk.

        Parameters
        ----------
        cond: :obj: `str`
            Indicate if the user want to print Precondtions, Postconditions,
             or Executions.
        verbose: bool
            Indicate if the user want to print the source code of the
            conditions.

        """
        cond_names = [f[:-3]
                      for f in listdir(join(self._conds_path, cond))
                      if isfile(join(join(self._conds_path, cond), f))
                      and f != "__init__.py"
                      and f[-3:] == ".py"]
        if verbose:
            for n in cond_names:
                print(colored(n, 'cyan'))
                print(self.get_function_source(cond, n))
        else:
            print("\n".join(cond_names))
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
                            ("layers", [l.dict() for l in self._layers.values()]),
                            ("raw", self._raw)])

    def read(self, path):
        """Reads a `Template` from disk.

        Parameters
        ----------
        path: str
            Path from which the template will be read.

        """
        with open(path) as t:
            template = json.load(t)
        # Reading layers
        self._name = template['Name']
        self._version = template['Version']
        self._timestamp = template['Timestamp']
        self._description = template['Description']
        self._raw = template['raw']
        self._functions = template['Functions']
        for layer in template['layers']:
            l = TLayer(layer['name'],
                       raw=self._raw,
                       lslice=layer['lslice'],
                       custom=layer['custom'])
            # Reading the structs
            structs = layer["structs"]
            # Reading fields
            for field in layer['fields']:
                ftype = field['type']
                if ftype[0] == str(int):
                    ftype = (int, ftype[1])
                elif ftype[0] == str(str):
                    ftype = (str, ftype[1])
                elif ftype[0] == str(bytes):
                    ftype = (bytes, ftype[1])
                f = TField(name=field['name'],
                           value=bytearray.fromhex(field['value']),
                           raw=self._raw,
                           tslice=field['slice'],
                           custom=field['custom'],
                           size=field['size'],
                           ftype=ftype,
                           frepr=field['frepr'])
                f.layer = l
                l.addfield(f)
            # Initialization of the structs
            for f in structs:
                l.add_struct(f,
                             structs[f]['fdeps'],
                             structs[f]['sb'],
                             structs[f]['exp'])
            self.addlayer(l)
