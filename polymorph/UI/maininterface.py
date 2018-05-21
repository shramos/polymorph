# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit import HTML
from polymorph.utils import capture, get_arpspoofer, set_ip_forwarding, readtemplate, readpcap
from polymorph.UI.tlistinterface import TListInterface
from polymorph.UI.templateinterface import TemplateInterface
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import os


class MainInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the starting interface, when no action has been carried out."""

    def __init__(self):
        # Constructor of the parent class
        super(MainInterface, self).__init__()
        # Class Attributes
        self._cap = None

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['capture', 'spoof', 'clear', 'import'])
        history = FileHistory(self._polym_path + '/.minterface_history')
        session = PromptSession(history=history)
        while True:
            try:
                command = session.prompt(HTML("<bold><red>PH</red> > </bold>"),
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
            elif command[0] in ["capture", "c"]:
                self._capture(command)
            elif command[0] in ["spoof", "s"]:
                self._spoof(command)
            elif command[0] in ["import", "i"]:
                self._import(command)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _capture(self, command):
        """Handles the capture command and the options."""

        def run_tlistinterface(tlist):
            """Runs the interface that handles the list of Templates."""
            tlistinterface = TListInterface(tlist, self._poisoner)
            tlistinterface.run()

        def capture_banner():
            """Shows a banner before capturing."""
            Interface._print_info("Waiting for packets...")
            print("(Press Ctr-C to exit)\n")

        def no_captured():
            """Shows no packets captured."""
            Interface._print_error("No packets have been captured.")

        # If not additional options
        if len(command) == 1:
            capture_banner()
            cap = capture()
            if cap:
                # Showing the new interface to the user
                run_tlistinterface(cap)
            else:
                no_captured()
            return
        # Parsing additional options
        cp = CommandParser(MainInterface._capture_opts())
        args = cp.parse(command)
        # Wrong arguments will return None
        if not args:
            Interface._argument_error()
            return
        # This variable handles the verbose option
        func = None
        # Print the help
        if args["-h"]:
            Interface.print_help(MainInterface.capture_help())
            return
        # Capture with verbose
        elif args["-v"]:
            func = MainInterface._print_v
        # Capture with lot of verbose
        elif args["-vv"]:
            func = MainInterface._print_vv
        # Capturing
        capture_banner()
        cap = capture(userfilter=args["-f"],
                      count=args["-c"],
                      time=args["-t"],
                      func=func)
        if cap:
            run_tlistinterface(cap)
        else:
            no_captured()

    @staticmethod
    def _print_v(packet):
        print(packet.summary())

    @staticmethod
    def _print_vv(packet):
        packet.show()

    @staticmethod
    def _capture_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-v": {"type": bool,
                       "default": False},
                "-vv": {"type": bool,
                        "default": False},
                "-c": {"type": int,
                       "default": 0},
                "-t": {"type": int,
                       "default": None},
                "-f": {"type": str,
                       "default": ""},
                "-file": {"type": str,
                          "default": ""}}
        return opts

    @staticmethod
    def capture_help():
        """Builds the help for the capture command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-f", "allows packet filtering using the BPF notation."),
            ("-c", "number of packets to capture."),
            ("-t", "stop sniffing after a given time."),
            ("-file", "read a .pcap file from disk."),
            ("-v", "verbosity level medium."),
            ("-vv", "verbosity level high.")
        ])
        return OrderedDict([
            ("name", "capture"),
            ("usage", "capture [-option]"),
            ("description", "Capture packets from a specific interface and transform them into a template list."),
            ("options", options)
        ])

    def _import(self, command):
        if len(command) == 1:
            Interface.print_help(MainInterface._import_help())
            return
        # Parsing additional options
        cp = CommandParser(MainInterface._import_opts())
        args = cp.parse(command)
        # Wrong arguments will return None
        if not args:
            Interface._argument_error()
            return
        # Importing a template
        if args["-h"]:
            Interface.print_help(MainInterface._import_help())
        elif args["-t"]:
            if os.path.isfile(args["-t"]):
                try:
                    template = readtemplate(args["-t"])
                    t = TemplateInterface(template, 0, self._poisoner)
                    t.run()
                except:
                    Interface._print_error("Wrong Template file")
            else:
                Interface._print_error("The file does not exist")
        elif args["-pcap"]:
            if os.path.isfile(args["-pcap"]):
                try:
                    tlist = readpcap(args["-pcap"])
                    tl = TListInterface(tlist, self._poisoner)
                    tl.run()
                except:
                    Interface._print_error("Wrong pcap file")
            else:
                Interface._print_error("The file does not exist")

    @staticmethod
    def _import_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-t": {"type": str,
                       "default": None},
                "-pcap": {"type": str,
                          "default": None},
                "-h": {"type": bool,
                       "default": False}}
        return opts

    @staticmethod
    def _import_help():
        """Builds the help for the capture command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-t", "path to a template to be imported."),
            ("-pcap", "path to a pcap file to be imported")

        ])
        return OrderedDict([
            ("name", "import"),
            ("usage", "import [-option]"),
            ("description", "Import different objects in the framework, such as templates or captures."),
            ("options", options)
        ])
