# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

import hexdump
from termcolor import colored
import sys
from polymorph.deps.prompt_toolkit.shortcuts import confirm
from polymorph.utils import set_ip_forwarding
from polymorph.utils import get_arpspoofer
from polymorph.UI.command_parser import CommandParser
from collections import OrderedDict
import os
from os.path import dirname
import polymorph


class Interface(object):
    EXIT = ['quit', 'exit', 'q']
    RET = ['return', 'back', 'b']

    def __init__(self):
        self._poisoner = None
        self._polym_path = dirname(polymorph.__file__)

    @staticmethod
    def print_help(hdict):
        print("Usage:", hdict['usage'])
        print("     ", hdict["description"])
        print("\n      Options:")
        for k in hdict["options"]:
            print('\t', k, '\t\t', hdict["options"][k], sep="")
        print("")

    @staticmethod
    def color_dump(raw, start, end=None):
        row = int(start / 16) * 77
        st = ((start % 16) * 3) + row + 10
        hd = hexdump.hexdump(raw, 'return')
        if end:
            srow = int(end / 16) * 77
            stop = ((end % 16) * 3) + srow + 10
            print(hd[:st], colored(hd[st:stop], 'cyan'),
                  hd[stop:], '\n', sep="")
        else:
            print(hd[:st], colored(hd[st:], 'cyan'), '\n', sep="")

    def exit_program(self):
        answer = confirm("Are you sure you want to exit? [y/N] ")
        if answer:
            if self._poisoner:
                set_ip_forwarding(0)
                Interface._print_info("Stopping the arp spoofer")
                self._poisoner.stop()
            print("\nBye Bye! See you soon!")
            sys.exit()

    def _spoof(self, command):
        """Handles the spoof command and the options."""
        # No command options
        if len(command) == 1:
            # Print the help
            Interface.print_help(Interface._spoof_help())
        else:
            # Parsing the command arguments
            cp = CommandParser(Interface._spoof_opts())
            args = cp.parse(command)
            if not args:
                Interface._argument_error()
                return
            # Print the help
            if args["-h"]:
                Interface.print_help(Interface._spoof_help())
            # Spoof between machines
            if args["-t"] and args["-g"]:
                # Set ip forwarding in Linux Operating systems
                set_ip_forwarding(1)
                try:
                    # Getting the poisoner
                    self._poisoner = get_arpspoofer(
                        args["-t"], args["-g"], args["-i"])
                    self._poisoner.start()
                    Interface._print_info(
                        "ARP spoofing started between %s and %s" % (args["-g"], args["-t"]))
                except:
                    Interface._print_error("Invalid target(s) or gateway")
                    set_ip_forwarding(0)
            else:
                Interface._print_error(
                    "Missing argument '-t' or '-g' (-h to show the options)")

    @staticmethod
    def _spoof_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-t": {"type": str,
                       "default": None},
                "-g": {"type": str,
                       "default": None},
                "-i": {"type": str,
                       "default": None}}

        return opts

    @staticmethod
    def _spoof_help():
        """Builds the help for the spoof command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-t", "targets to perform the ARP spoofing. Separated by ','"),
            ("-g", "gateway to perform the ARP spoofing"),
            ("-i", "network interface.")
        ])
        return OrderedDict([
            ("name", "spoof"),
            ("usage", "spoof -t <targets> -g <gateway>"),
            ("description", "Performs an ARP spoofing between machines in the network."),
            ("options", options)
        ])

    @staticmethod
    def _clear():
        os.system('clear')

    @staticmethod
    def _wrong_command():
        Interface._print_error("Wrong command (tab to show the commands)")

    @staticmethod
    def _argument_error():
        Interface._print_error("Wrong argument (-h to show the options)")

    @staticmethod
    def _print_error(text):
        print("[", colored("!", 'red', attrs=['bold']), "]",
              " %s\n" % text, sep="")

    @staticmethod
    def _print_info(text):
        print("[", colored("+", 'green', attrs=['bold']), "]",
              " %s\n" % text, sep="")
