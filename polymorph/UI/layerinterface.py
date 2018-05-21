# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from polymorph.deps.prompt_toolkit import PromptSession
from polymorph.deps.prompt_toolkit import HTML
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from termcolor import colored
from polymorph.tfield import TField
from polymorph.UI.fieldinterface import FieldInterface
import hexdump
from polymorph.deps.prompt_toolkit.history import FileHistory
from polymorph.deps.prompt_toolkit.completion import WordCompleter
from polymorph.deps.prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from polymorph.deps.prompt_toolkit.shortcuts import CompleteStyle
import construct


class LayerInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the tlist interface, when the user already has a packet capture."""

    def __init__(self, layer, tindex, poisoner=None):
        """Initialization method of the class.

        Parameters
        ----------
        layer : obj:`TLayer`
            The layer object.
        tindex : int
            The index of the `Template` of the `TLayer`.
        poisoner : obj:`ARPpoisones`
            The poisoner object, if exist

        """
        # Constructor of the parent class
        super(LayerInterface, self).__init__()
        # Class Attributes
        self._l = layer
        self._tindex = tindex
        self._poisoner = poisoner

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['show', 'name', 'field', 'fields',
                                   'dump', 'recalculate', 'clear', 'back'])
        history = FileHistory(self._polym_path + '/.linterface_history')
        session = PromptSession(history=history)
        while True:
            try:
                command = session.prompt(HTML("<bold>PH:cap/t%d/<red>%s</red> > </bold>" %
                                              (self._tindex, self._l.name)),
                                         completer=completer,
                                         complete_style=CompleteStyle.READLINE_LIKE,
                                         auto_suggest=AutoSuggestFromHistory(),
                                         enable_history_search=True)
            except KeyboardInterrupt:
                self.exit_program()
                continue
            # Argument parsing
            command = command.split(" ")
            if command[0] in self.EXIT:
                self.exit_program()
            elif command[0] in self.RET:
                break
            elif command[0] in ["s", "show"]:
                self._show(command)
            elif command[0] == "name":
                self._name(command)
            elif command[0] in ["field", "f"]:
                self._field(command)
            elif command[0] in ["fields", "fs"]:
                self._fields(command)
            elif command[0] in ["dump", "d"]:
                self._dump(command)
            elif command[0] in ["recalculate", "r"]:
                self._recalculate(command)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _show(self, command):
        """Shows the contents of the `TLayer`"""
        if len(command) == 1:
            self._l.show()
            return
        # Parsing the arguemnts
        cp = CommandParser(LayerInterface._show_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(LayerInterface._show_help())
        # Shows a particular field
        elif args["-f"]:
            self._l.getlayer(args["-f"]).show()

    @staticmethod
    def _show_help():
        """Builds the help for the show command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-f", "shows a particular field.")
        ])
        return OrderedDict([
            ("name", "show"),
            ("usage", "show [-option]"),
            ("description", "Prints information about the layer."),
            ("options", options)
        ])

    @staticmethod
    def _show_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-f": {"type": str,
                       "default": None}}
        return opts

    def _name(self, command):
        """Manages the name of the `TLayer`."""
        if len(command) == 1:
            print(self._l.name, '\n')
            return
        # Parsing the arguments
        cp = CommandParser(LayerInterface._name_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(LayerInterface._name_help())
        # Add a new name
        elif args["-n"]:
            self._l.name = args["-n"]
            Interface._print_info("New name %s added" % args['-n'])

    @staticmethod
    def _name_help():
        """Builds the help for the name command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-n", "set a new name to the layer.")
        ])
        return OrderedDict([
            ("name", "name"),
            ("usage", "name [-option]"),
            ("description", "Manage the name of the layer."),
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

    def _fields(self, command):
        """Show all the fields in the layer."""
        if len(command) == 1:
            print(colored("\n".join(self._l.fieldnames()), 'cyan'), "\n")
            return
        # Parsing arguments
        cp = CommandParser(LayerInterface._fields_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(LayerInterface._fields_help())
        # Prints the custom fields
        elif args["-c"]:
            cfields = [f.name for f in self._l.customfields()]
            print(colored("\n".join(cfields), 'cyan'), "\n")

    @staticmethod
    def _fields_help():
        """Builds the help for the fields command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-c", "prints the custom fields.")
        ])
        return OrderedDict([
            ("name", "fields"),
            ("usage", "fields [-option]"),
            ("description", "Prints the fields of the layer."),
            ("options", options)
        ])

    @staticmethod
    def _fields_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-c": {"type": bool,
                       "default": False}}
        return opts

    def _field(self, command):
        """Manages the access an creation of `TField`."""
        if len(command) == 1:
            Interface.print_help(LayerInterface._field_help())
        elif len(command) == 2 and command[1].lower() in self._l.fieldnames():
            fi = FieldInterface(self._l.getfield(
                command[1].lower()), self._tindex, self._l.name, self._poisoner)
            fi.run()
        else:
            cp = CommandParser(LayerInterface._field_opts())
            args = cp.parse(command)
            if not args:
                Interface._argument_error()
                return
            # Print the help
            if args["-h"]:
                Interface.print_help(LayerInterface._field_help())
            # Adds a new field
            elif args["-a"]:
                Interface.color_dump(self._l.raw, self._l.slice.start)
                start = input("Start byte of the custom field: ")
                end = input("End byte of the custom field: ")
                if not start.isdecimal() or not end.isdecimal():
                    Interface._print_error(
                        "The start or end byte is not a number")
                    return
                else:
                    fslice = slice(int(start), int(end))
                    fvalue = self._l.raw[fslice]
                    fsize = len(fvalue)
                    new_field = TField(name=args["-a"],
                                       value=fvalue,
                                       tslice=str(fslice).encode().hex(),
                                       custom=True,
                                       size=fsize,
                                       raw=self._l.raw.hex(),
                                       layer=self._l)
                    # Set the type
                    ftype = input("Field type [int/str/bytes/hex]: ")
                    if ftype == "int":
                        new_field.to_int()
                    elif ftype == "str":
                        new_field.to_str()
                    elif ftype == "hex":
                        new_field.to_hex()
                    elif ftype == "bytes":
                        new_field.to_bytes()
                    # Add the field to the layer
                    self._l.addfield(new_field)
                    Interface._print_info(
                        "Field %s added to the layer" % args['-a'])
            # Deletes a field from the layer
            elif args["-d"]:
                del_field = self._l.getfield(args["-d"])
                if del_field:
                    self._l.delfield(del_field)
                    Interface._print_info(
                        "Field %s deleted from the layer" % args["-d"])
                else:
                    Interface._print_error(
                        "The field %s is not in the layer" % args["-d"])

    @staticmethod
    def _field_help():
        """Builds the help for the field command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "adds a new field to the layer."),
            ("-d", "deletes a custom field from the layer.")
        ])
        return OrderedDict([
            ("name", "field"),
            ("usage", "field <name> [-option]"),
            ("description", "access and manage the fields of the layer."),
            ("options", options)
        ])

    @staticmethod
    def _field_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-a": {"type": str,
                       "default": None},
                "-d": {"type": str,
                       "default": None}}
        return opts

    def _dump(self, command):
        """Dumps the layer bytes in different formats."""
        if len(command) == 1:
            Interface.color_dump(self._l.raw, self._l.slice.start)
            return
        # Parsing the arguments
        cp = CommandParser(LayerInterface._dump_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        if args["-hex"]:
            Interface.color_dump(self._l.raw, self._l.slice.start)
        elif args["-b"]:
            print(str(self._l.raw[self._l.slice.start:]), '\n')
        elif args["-hexstr"]:
            d = hexdump.dump(self._l.raw).split(" ")
            print(" ".join(d[self._l.slice.start:]), '\n')
        elif args["-h"]:
            Interface.print_help(LayerInterface._dump_help())

    @staticmethod
    def _dump_help():
        """Builds the help for the dump command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-hex", "dump the packet bytes encoded in hexadecimal."),
            ("-b", "dump the packet bytes without encoding."),
            ("-hexstr", "dump the packet bytes as an hexadecimal stream.")
        ])
        return OrderedDict([
            ("name", "dump"),
            ("usage", "dump [-option]"),
            ("description", "Dumps the layer bytes in different formats."),
            ("options", options)
        ])

    @staticmethod
    def _dump_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-hex": {"type": bool,
                         "default": False},
                "-b": {"type": bool,
                       "default": False},
                "-hexstr": {"type": bool,
                            "default": False}}
        return opts

    def _recalculate(self, command):
        """Manages all the recalculate options for the fields of the layer."""
        if len(command) == 1:
            Interface.print_help(LayerInterface._recalculate_help())
            return
        # Parsing the arguments
        cp = CommandParser(LayerInterface._recalculate_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(LayerInterface._recalculate_help())
        # Adds a new recalculate expression
        elif args["-f"] and args["-sb"] and args["-e"]:
            fields = LayerInterface._extrac_deps(args["-sb"], args["-e"])
            if fields:
                try:
                    self._l.add_struct(
                        args["-f"], fields, args["-sb"], args["-e"])
                    Interface._print_info(
                        "Struct added to field %s" % args["-f"])
                except:
                    Interface._print_error(
                        "Wrong fields or wrong syntax referring to the fields")
                    return
            else:
                Interface._print_error(
                    "Wrong syntax for referring to the fields. Please use 'this.field' syntax")
        # Tests a created struct
        elif args["-t"] and len(command) == 3:
            if self._l.is_struct(args["-t"]):
                try:
                    print(self._l.test_struct(args["-t"]), "\n")
                except construct.core.StreamError as e:
                    Interface._print_error(
                        "The Struct is not well formed. Please check the fields and their type.\n%s" % str(e))
            else:
                Interface._print_error(
                    "The Struct %s is not in the layer" % args['-t'])
        # Show the struct for a particular field
        elif args["-s"] and len(command) == 3:
            self._l.show_structs(args["-s"])
        # Deletes a struct for a field
        elif args["-d"] and len(command) == 3:
            if self._l.is_struct(args["-d"]):
                self._l.del_struct(args["-d"])
                Interface._print_info("Struct deleted for %s" % args["-d"])
            else:
                self._print_error(
                    "The Struct %s is not in the layer" % args["-d"])

    @staticmethod
    def _extrac_deps(start_byte, expression):
        patterns = start_byte.split(" ") + expression.split(" ")
        fields = []
        for p in patterns:
            if 'this.' in p and p[5:] not in fields:
                fields.append(p[5:])
        return fields

    @staticmethod
    def _recalculate_help():
        """Builds the help for the recalculate command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-f", "field to be recalculated"),
            ("-sb", "start byte of the field that you want to recalculate."),
            ("-e", "expression that recalculates the field"),
            ("-t", "tests a previously created structure"),
            ("-s", "shows the struct for a particular field"),
            ("-d", "deletes a struct from a field.")
        ])
        return OrderedDict([
            ("name", "recalculate"),
            ("usage", "recalculate <-option>"),
            ("description", "Creates a structure that relates a field to other fields of the layer, so that its value "
                            "can be calculated dynamically at run time."),
            ("options", options)
        ])

    @staticmethod
    def _recalculate_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-s": {"type": str,
                       "default": None},
                "-f": {"type": str,
                       "default": None},
                "-sb": {"type": str,
                        "default": None},
                "-e": {"type": str,
                       "default": None},
                "-d": {"type": str,
                       "default": None},
                "-t": {"type": str,
                       "default": None}}
        return opts
