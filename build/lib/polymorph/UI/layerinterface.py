# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import PromptSession
from prompt_toolkit import HTML
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from termcolor import colored
from polymorph.tfield import TField
from polymorph.UI.fieldinterface import FieldInterface
from polymorph.converter import Converter
from polymorph.ftype import Ftype
import hexdump
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
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
                                   'dump', 'struct', 'clear', 'back'])
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
            try:
                command = command.split(" ")
                if command[0] in self.EXIT:
                    self.exit_program()
                elif command[0] in self.RET:
                    break
                elif command[0] in ["s", "show"]:
                    self._show(command)
                elif command[0] == "name":
                    print(self._l.name, '\n')
                elif command[0] in ["field", "f"]:
                    self._field(command)
                elif command[0] in ["fields", "fs"]:
                    print(colored("\n".join(self._l.fieldnames()), 'cyan'), "\n")
                elif command[0] in ["dump", "d"]:
                    self._dump(command)
                elif command[0] in ["struct", "st"]:
                    self._struct(command)
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
            self._l.getfield(args["-f"]).show()

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
                Interface.color_dump(self._l.pkt_raw, self._l.slice.start)
                start = input("Start byte of the custom field: ")
                end = input("End byte of the custom field: ")
                if not start.isdecimal() or not end.isdecimal():
                    Interface._print_error(
                        "The start or end byte is not a number")
                    return
                else:
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
                    ftype = Ftype(int(ftype) - 1)
                    fslice = slice(int(start), int(end))
                    pkt_raw = self._l.pkt_raw
                    fsize = fslice.stop - fslice.start
                    try:
                        cv = Converter()
                        frepr = cv.get_frepr(
                            ftype, pkt_raw[fslice], fsize, fmask, args["-a"])
                    except Exception as e:
                        print(e)
                        Interface._print_error(
                            "The value of the field in bytes is wrong")
                        return
                    new_field = TField(fname=args["-a"],
                                       fslice=fslice,
                                       fsize=fsize,
                                       pkt_raw=self._l.pkt_raw,
                                       layer=self._l,
                                       trepr="",
                                       ttype=None,
                                       tmask=fmask,
                                       ftype=ftype,
                                       frepr=frepr)
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
            Interface.color_dump(self._l.pkt_raw, self._l.slice.start)
            return
        # Parsing the arguments
        cp = CommandParser(LayerInterface._dump_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        if args["-hex"]:
            Interface.color_dump(self._l.pkt_raw, self._l.slice.start)
        elif args["-b"]:
            print(str(self._l.pkt_raw[self._l.slice.start:]), '\n')
        elif args["-hexstr"]:
            d = hexdump.dump(self._l.pkt_raw).split(" ")
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

    def _struct(self, command):
        """Manages all the struct options for the fields of the layer."""
        if len(command) == 1:
            Interface.print_help(LayerInterface._struct_help())
            return
        # Parsing the arguments
        cp = CommandParser(LayerInterface._struct_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(LayerInterface._struct_help())
        # Adds a new struct to the field
        elif args["-f"] and args["-e"]:
            if args["-sb"]:
                sb = args["-sb"]
            else:
                sb = str(self._l.getfield(args["-f"]).slice.start)
            # We obtain the references to fields in the layer
            fields = [e.replace("this.", "")
                      for e in sb.split(" ") + args["-e"].split(" ")
                      if "this." in e]
            # Remove duplicate fields
            fields = list(dict.fromkeys(fields))
            if fields:
                try:
                    self._l.add_struct(
                        args["-f"], fields, sb, args["-e"])
                    Interface._print_info(
                        "Struct added to field %s" % args["-f"])
                except Exception as e:
                    print(e)
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
                        "The Struct is not well formed. "
                        "Please check the fields and their type.\n%s" % str(e))
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
    def _struct_help():
        """Builds the help for the struct command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-f", "name of the field to be recalculated"),
            ("-sb", "Expression that calculates the position of the first"
             "byte of the field"),
            ("-e", "Expression that calculates the length of the field"),
            ("-t", "name of a previously created structure to be tested"),
            ("-s", "name of a specific field to show the structures it has associated"),
            ("-d", "name of a field to delete the associated structures")
        ])
        return OrderedDict([
            ("name", "struct"),
            ("usage", "struct <-option>"),
            ("description", "Creates a structure that relates a field to"
             "other fields of the layer, so that its value can be calculated"
             "dynamically at run time."),
            ("options", options)
        ])

    @staticmethod
    def _struct_opts():
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
