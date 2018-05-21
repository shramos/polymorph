# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from polymorph.deps.prompt_toolkit import PromptSession
from polymorph.deps.prompt_toolkit import HTML
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from polymorph.deps.prompt_toolkit.history import FileHistory
from polymorph.deps.prompt_toolkit.completion import WordCompleter
from polymorph.deps.prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from polymorph.deps.prompt_toolkit.shortcuts import CompleteStyle


class FieldInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the field interface, when the user already has a packet capture."""

    def __init__(self, field, index, layername, poisoner=None):
        """Initialization method of the class.

        Parameters
        ----------
        field : obj:`TField`
            `TField` object.
        index : int
            Index of the `Template` that contains the `TField`.
        layername: :obj:`str`
            Name of the `TLayer` that contains the `TField`.
        poisoner : :obj:`ARPpoisoner`
            Poisoning object.

        """
        # Constructor of the parent class
        super(FieldInterface, self).__init__()
        # Class Attributes
        self._f = field
        self._tindex = index
        self._lname = layername
        self._poisoner = poisoner

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['value', 'type', 'show', 'name', 'slice',
                                   'custom', 'size', 'dump', 'clear', 'back'])
        history = FileHistory(self._polym_path + '/.finterface_history')
        session = PromptSession(history=history)
        while True:
            try:
                command = session.prompt(HTML("<bold>PH:cap/t%d/%s/<red>%s</red> > </bold>" %
                                              (self._tindex, self._lname, self._f.name)),
                                         completer=completer,
                                         complete_style=CompleteStyle.READLINE_LIKE,
                                         auto_suggest=AutoSuggestFromHistory(),
                                         enable_history_search=True)
            except KeyboardInterrupt:
                self.exit_program()
                continue
            command = command.split(" ")
            if command[0] in self.EXIT:
                self.exit_program()
            elif command[0] in self.RET:
                break
            elif command[0] in ['t', 'type']:
                self._type(command)
            elif command[0] in ['v', 'value']:
                self._value(command)
            elif command[0] in ['s', 'show']:
                self._show(command)
            elif command[0] == 'name':
                self._name(command)
            elif command[0] == "slice":
                print(self._f.slice, '\n')
            elif command[0] == "custom":
                self._custom(command)
            elif command[0] == "size":
                print(self._f.size, '\n')
            elif command[0] in ['d', 'dump']:
                Interface.color_dump(self._f.raw,
                                     self._f.slice.start,
                                     self._f.slice.stop)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _type(self, command):
        """Manages the type of the `TField`"""
        if len(command) == 1:
            print(self._f.type, '\n')
            return
        # Parsing the arguments
        cp = CommandParser(FieldInterface._type_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(FieldInterface._type_help())
        # Add a new type
        elif args["-a"]:
            if args["-a"] == "hex":
                self._f.to_hex()
                Interface._print_info("New type added")
            elif args["-a"] == "bytes":
                self._f.to_bytes()
                Interface._print_info("New type added")
            elif args["-a"] == "str":
                self._f.to_str()
                Interface._print_info("New type added")
            elif args["-a"] == "int":
                if args["-o"] in ['big', 'little']:
                    self._f.to_int(args["-o"])
                    Interface._print_info("New type added")
                else:
                    Interface._print_error(
                        "Wrong order. Please select big or little")
            else:
                Interface._print_error(
                    "Wrong type. Please choose between ('hex', 'bytes', 'str', 'int')")

    @staticmethod
    def _type_help():
        """Builds the help for the type command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "add a new type to the field ('hex', 'str', 'bytes', 'int')"),
            ("-o", "order for int type ('big', 'little')")
        ])
        return OrderedDict([
            ("name", "type"),
            ("usage", "type [-option]"),
            ("description", "Manages the field type."),
            ("options", options)
        ])

    @staticmethod
    def _type_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-a": {"type": str,
                       "default": None},
                "-o": {"type": str,
                       "default": 'big'}}
        return opts

    def _value(self, command):
        """Manages the value of the `TField`."""
        if len(command) == 1:
            print(self._f.value, '\n')
            return
        # Parsing the arguments
        cp = CommandParser(FieldInterface._value_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(FieldInterface._value_help())
        # Prints the value encoded in hex
        if args["-hex"]:
            print(self._f.valuehex, '\n')
        # Prints the value encoded in bytes
        elif args["-b"]:
            print(self._f.valuebytes, '\n')
        # Adds a new value
        elif args["-a"]:
            if args["-t"] == 'str':
                self._f.value = args["-a"]
                Interface._print_info("New value added to the field")
            elif args["-t"] == 'int':
                self._f.value = int(args["-a"])
                Interface._print_info("New value added to the field")
            elif args["-t"] == 'hex':
                self._f.value = args["-a"]
                Interface._print_info("New value added to the field")
            elif args["-t"] == 'bytes':
                self._f.value = args["-a"].encode()
                Interface._print_info("New value added to the field")
            else:
                Interface._print_error(
                    "Wrong type. Please choose between ('hex', 'bytes', 'str', 'int')")

    @staticmethod
    def _value_help():
        """Builds the help for the value command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "add a new value to the field"),
            ("-t", "type of the value ('hex', 'bytes', 'str', 'int'). By default 'str'."),
            ("-hex", "prints the value encoded in hex."),
            ("-b", "prints the value encoded in bytes.")
        ])
        return OrderedDict([
            ("name", "value"),
            ("usage", "value [-option]"),
            ("description", "Manages the field value."),
            ("options", options)
        ])

    @staticmethod
    def _value_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-a": {"type": str,
                       "default": None},
                "-t": {"type": str,
                       "default": 'str'},
                "-hex": {"type": bool,
                         "default": False},
                "-b": {"type": bool,
                       "default": False}}
        return opts

    def _show(self, command):
        """Pretty printing of the `TField`."""
        if len(command) == 1:
            self._f.show()

    def _name(self, command):
        """Manages the name of the field."""
        if len(command) == 1:
            print(self._f.name, '\n')
            return
        # Parsing field arguments
        cp = CommandParser(FieldInterface._name_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(FieldInterface._name_help())
        # Adding a new name to the field
        elif args["-n"]:
            self._f.name = args["-n"]
            Interface._print_info(
                "New name %s added to the field" % args["-n"])

    @staticmethod
    def _name_help():
        """Builds the help for the name command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-n", "set a new name to the field.")
        ])
        return OrderedDict([
            ("name", "name"),
            ("usage", "name [-option]"),
            ("description", "Manage the name of the field."),
            ("options", options)
        ])

    @staticmethod
    def _name_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-n": {"type": str,
                       "default": None}}
        return opts

    def _custom(self, command):
        """Manages the custom parameter of the field."""
        if len(command) == 1:
            print(self._f.is_custom(), '\n')
            return
        # Parsing the arguments
        cp = CommandParser(FieldInterface._custom_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(FieldInterface._custom_help())
        # Sets custom to True
        elif args["-set"]:
            self._f.set_custom()
            Interface._print_info("Custom set to True")
        # Sets custom to False
        elif args["-unset"]:
            self._f.unset_custom()
            Interface._print_info("Custom set to False")

    @staticmethod
    def _custom_help():
        """Builds the help for the custom command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-set", "set the field as custom."),
            ("-unset", "unset the field as custom")
        ])
        return OrderedDict([
            ("name", "custom"),
            ("usage", "custom [-option]"),
            ("description", "Manage the custom property of the field."),
            ("options", options)
        ])

    @staticmethod
    def _custom_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-set": {"type": bool,
                         "default": False},
                "-unset": {"type": bool,
                           "default": False}}
        return opts
