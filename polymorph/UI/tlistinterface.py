# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import PromptSession
from prompt_toolkit import HTML
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from polymorph.UI.templateinterface import TemplateInterface
import os
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.shortcuts import CompleteStyle
import polymorph
from os.path import dirname, join


class TListInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the tlist interface, when the user already has a packet capture."""

    def __init__(self, tlist, poisoner=None):
        """Initialization method of the class.

        Parameters
        ----------
        tlist : obj:`TList`
            The list of `Templates` previously captured.
        poisoner : obj:`ARPpoisoner`
            The arp poisoner object, if any.

        """
        # Constructor of the parent class
        super(TListInterface, self).__init__()
        # Class Attributes
        self._t = tlist
        self._poisoner = poisoner
        self._polym_path = dirname(polymorph.__file__)

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['show', 'dissect', 'template', 'wireshark',
                                   'clear', 'back'])
        history = FileHistory(self._polym_path + '/.tlinterface_history')
        session = PromptSession(history=history)
        while True:
            try:
                command = session.prompt(HTML("<bold>PH:<red>cap</red> > </bold>"),
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
            elif command[0] in ["show", "s"]:
                self._show(command)
            elif command[0] == "dissect":
                self._dissect(command)
            elif command[0] in ["template", "t"]:
                self._template(command)
            elif command[0] in ["wireshark", "w"]:
                self._wireshark(command)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _show(self, command):
        """Shows the list of `Template`."""
        if len(command) == 1:
            self._t.show()
            return
        # Parsing arguments
        cp = CommandParser(TListInterface._show_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TListInterface._show_help())
        # Print a particular Template
        elif args["-t"]:
            self._t[args["-t"]].show()

    @staticmethod
    def _show_help():
        """Builds the help for the show command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-t", "show a particular template.")
        ])
        return OrderedDict([
            ("name", "show"),
            ("usage", "show [-option]"),
            ("description", "Prints information about the list of templates."),
            ("options", options)
        ])

    @staticmethod
    def _show_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-t": {"type": int,
                       "default": None}}
        return opts

    def _dissect(self, command):
        """Dissects the Template List with the Tshark dissectors."""
        if len(command) == 1:
            Interface._print_info("Dissecting the packets...")
            self._t[-1]
            Interface._print_info("Finished!")
            return
        # Parsing the arguments
        cp = CommandParser(TListInterface._dissect_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Prints the help
        if args["-h"]:
            Interface.print_help(TListInterface._dissect_help())
        # Dissects until a particular Template
        elif args["-t"]:
            Interface._print_info("Dissecting packets until %d" % args["-t"])
            self._t[args["-t"]]

    @staticmethod
    def _dissect_help():
        """Builds the help for the dissect command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-t", "dissects until a particular template.")
        ])
        return OrderedDict([
            ("name", "dissect"),
            ("usage", "dissect [-option]"),
            ("description",
             "Dissects the captured packets with the Tshark dissectors and generates a template from the packet."),
            ("options", options)
        ])

    @staticmethod
    def _dissect_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-t": {"type": int,
                       "default": None}}
        return opts

    def _template(self, command):
        """Manages the access to a particular `Template` in the list."""
        if len(command) == 1:
            Interface.print_help(TListInterface._template_help())
        elif len(command) == 2:
            # Print the help
            if command[1] == "-h":
                Interface.print_help(TListInterface._template_help())
            # Select a particular Template
            elif command[1].isdecimal():
                index = int(command[1])
                ti = TemplateInterface(self._t[index], index, self._poisoner)
                ti.run()
            else:
                Interface._argument_error()
        else:
            Interface._argument_error()

    @staticmethod
    def _template_help():
        """Builds the help for the show command."""
        options = OrderedDict([
            ("-h", "prints the help."),
        ])
        return OrderedDict([
            ("name", "template"),
            ("usage", "template <num>"),
            ("description", "Access the content of a particular template."),
            ("options", options)
        ])

    def _wireshark(self, command):
        """Opens Wireshark with the actual `Template` List in pcap format."""
        if len(command) == 1:
            Interface._print_info("Opening Wireshark...")
            os.system("nohup wireshark %s &" %
                      join(self._polym_path, ".tmp.pcap"))
            return
        # Parsing arguments
        cp = CommandParser(TListInterface._wireshark_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TListInterface._wireshark_help())
        # Select a new path for the Wireshark binary
        elif args["-p"]:
            Interface._print_info("Opening Wireshark...")
            os.system("nohup %s %s &" %
                      (args["-p"], join(self._polym_path, ".tmp.pcap")))

    @staticmethod
    def _wireshark_help():
        """Builds the help for the wireshark command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-p", "indicate a new path to the wireshark binary.")
        ])
        return OrderedDict([
            ("name", "wireshark"),
            ("usage", "wireshark [-option]"),
            ("description", "Opens the captured file with Wireshark."),
            ("options", options)
        ])

    @staticmethod
    def _wireshark_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-p": {"type": str,
                       "default": None}}
        return opts
