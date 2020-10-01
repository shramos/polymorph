# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import PromptSession
from prompt_toolkit import HTML
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
from polymorph.converter import Converter
from polymorph.ftype import Ftype


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
                                   'size', 'dump', 'clear', 'back'])
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
            try:
                command = command.split(" ")
                if command[0] in self.EXIT:
                    self.exit_program()
                elif command[0] in self.RET:
                    break
                elif command[0] in ['v', 'value']:
                    self._value(command)
                elif command[0] in ['s', 'show']:
                    self._show(command)
                elif command[0] == 'name':
                    print(self._f.name, '\n')
                elif command[0] == "slice":
                    print(self._f.slice, '\n')
                elif command[0] == "type":
                    self._type(command)
                elif command[0] == "size":
                    print(self._f.size, '\n')
                elif command[0] in ['d', 'dump']:
                    Interface.color_dump(self._f.pkt_raw,
                                         self._f.slice.start,
                                         self._f.slice.stop)
                elif command[0] == "clear":
                    Interface._clear()
                elif command[0] == "":
                    continue
                else:
                    Interface._wrong_command()
            except SystemExit:
                raise
            except Exception as e:
                Interface._print_error(
                    "Exception: Error processing the previous command. More info:")
                print(e)

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
            print(self._f.hex(), '\n')
        # Prints the value encoded in bytes
        elif args["-b"]:
            print(self._f.raw, '\n')

    @staticmethod
    def _value_help():
        """Builds the help for the value command."""
        options = OrderedDict([
            ("-h", "prints the help."),
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
                "-hex": {"type": bool,
                         "default": False},
                "-b": {"type": bool,
                       "default": False}}
        return opts

    def _show(self, command):
        """Pretty printing of the `TField`."""
        if len(command) == 1:
            self._f.show()

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
            ftype = input("\n1: FT_INT_BE\n"
                          "2: FT_INT_LE\n"
                          "3: FT_STRING\n"
                          "4: FT_BYTES\n"
                          "5: FT_BIN_BE\n"
                          "6: FT_BIN_LE\n"
                          "7: FT_HEX\n"
                          "8: FT_ETHER\n"
                          "9: FT_IPv4\n"
                          "10: FT_IPv6\n"
                          "11: FT_ABSOLUTE_TIME\n"
                          "12: FT_RELATIVE_TIME\n"
                          "13: FT_EUI64\n\n"
                          "Select the type of the field: "
                          )
            if not ftype.isdecimal() or int(ftype) > 12 or int(ftype) < 0:
                Interface._print_error(
                    "Select a number between 1 and 12")
                return
            if int(ftype) in [5, 6]:
                fmask = input("Select the bitmask (ie: 11110000): ")
                if not fmask.isdecimal():
                    Interface._print_error(
                        "Select a binary number")
                    return
                fmask = int(fmask, 2)
            else:
                fmask = 0
            try:
                ftype = Ftype(int(ftype) - 1)
                cv = Converter()
                frepr = cv.get_frepr(
                    ftype, self._f.raw, self._f.size, fmask, self._f.name)
            except Exception as e:
                print(e)
                Interface._print_error(
                    "The value of the field in bytes is wrong")
                return
            self._f._ftype = ftype
            self._f._frepr = frepr
            Interface._print_info(
                "New type %s added to the field." % str(ftype))

    @staticmethod
    def _type_help():
        """Builds the help for the type command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "change the type of field.")
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
                "-a": {"type": bool,
                       "default": False}}
        return opts
