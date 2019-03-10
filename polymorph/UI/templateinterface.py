# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.UI.interface import Interface
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.shortcuts import confirm, CompleteStyle
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from collections import OrderedDict
from polymorph.UI.command_parser import CommandParser
from polymorph.UI.layerinterface import LayerInterface
from polymorph.tlayer import TLayer
from polymorph.interceptor import Interceptor
from termcolor import colored
import hexdump
import os
from os.path import dirname, join
import importlib
import polymorph.conditions
import platform
from shutil import copyfile


class TemplateInterface(Interface):
    """This class is responsible for parsing and respond to user commands in
    the Template interface, when the user already select a particular Template."""

    def __init__(self, template, index, poisoner=None):
        """Initialization method of the class.

        Parameters
        ----------
        template: obj:`Template`
            The selected `Template` object.
        index: int
            The index of the `Template` in the `TList`
        poisoner: obj:`ARPpoisoning`
            The poisoning object, if any.

        """
        # Constructor of the parent class
        super(TemplateInterface, self).__init__()
        # Class Attributes
        self._t = template
        self._index = index
        self._poisoner = poisoner
        self._conds_path = dirname(polymorph.conditions.__file__)

    def run(self):
        """Runs the interface and waits for user input commands."""
        completer = WordCompleter(['show', 'name', 'layer', 'dump', 'layers',
                                   'preconditions', 'postconditions', 'executions',
                                   'intercept', 'timestamp', 'version', 'save',
                                   'description', 'spoof', 'clear', 'back'])
        # Initialization of the command history
        history = FileHistory(join(self._polym_path, '.tinterface_history'))
        session = PromptSession(history=history)
        while True:
            try:
                command = session.prompt(HTML("<bold>PH:cap/<red>t%d</red> > </bold>" %
                                              self._index),
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
            elif command[0] == "name":
                self._name(command)
            elif command[0] in ["dump", "d"]:
                self._dump(command)
            elif command[0] in ["layer", "l"]:
                self._layer(command)
            elif command[0] in ['precs', 'preconditions']:
                self._conditions(command, 'preconditions')
            elif command[0] in ['posts', 'postconditions']:
                self._conditions(command, 'postconditions')
            elif command[0] in ['execs', 'executions']:
                self._conditions(command, 'executions')
            elif command[0] in ["show", "s"]:
                self._show(command)
            elif command[0] in ["intercept", "i"]:
                self._intercept(command)
            elif command[0] in ["layers", "ls"]:
                self._layers(command)
            elif command[0] == "timestamp":
                print(self._t.timestamp, '\n')
            elif command[0] == "version":
                self._version(command)
            elif command[0] in ['desc', 'description']:
                self._description(command)
            elif command[0] == "save":
                self._save(command)
            elif command[0] in ["spoof"]:
                self._spoof(command)
            elif command[0] == "clear":
                Interface._clear()
            elif command[0] == "":
                continue
            else:
                Interface._wrong_command()

    def _name(self, command):
        """Manages the name of the `Template`."""
        if len(command) == 1:
            print(self._t.name, '\n')
            return
        # Parsing the arguments
        cp = CommandParser(TemplateInterface._name_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._name_help())
        # Set a new name
        elif args["-n"]:
            self._t.name = args["-n"]
            Interface._print_info("New name added: %s" % args["-n"])

    @staticmethod
    def _name_help():
        """Builds the help for the name command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-n", "set a new name to the template.")
        ])
        return OrderedDict([
            ("name", "name"),
            ("usage", "name [-option]"),
            ("description", "Manage the name of the Template."),
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

    def _dump(self, command):
        """Dumps the packet/template bytes in different formats."""
        if len(command) == 1:
            hexdump.hexdump(self._t.raw)
            print("")
            return
        # Parsing the arguments
        cp = CommandParser(TemplateInterface._dump_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        if args["-hex"]:
            hexdump.hexdump(self._t.raw)
            print("")
        elif args["-b"]:
            print(str(self._t.raw), "\n")
        elif args["-hexstr"]:
            print(hexdump.dump(self._t.raw), "\n")
        elif args["-h"]:
            Interface.print_help(TemplateInterface._dump_help())

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
            ("description", "Dumps the packet bytes in different formats."),
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

    def _conditions(self, command, cond):
        """Manages the preconditions, postconditions and executions for a
        particular `Template`."""
        if len(command) == 1:
            self._t.show_conditions(cond)
            return
        # Parsing the arguments
        cp = CommandParser(TemplateInterface._conditions_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        if len(command) == 2:
            # Print the help
            if args['-h']:
                Interface.print_help(
                    TemplateInterface._conditions_help(cond))
            # Show the source code
            elif args['-s']:
                self._t.show_conditions(cond, verbose=True)
            # Show all conditions on disk
            elif args['-sa']:
                self._t.show_all_conds(cond)
            # Show all conditions source on disk
            elif args['-sas']:
                self._t.show_all_conds(cond, verbose=True)
        else:
            # Select a specific condition
            if args['-c']:
                if args['-s']:
                    self._t.show_conditions(cond, args['-c'], True)
                elif args['-p']:
                    try:
                        index = int(args['-p'])
                        if index >= 0 and index < len(self._t._functions[cond]):
                            self._t.change_cond_pos(cond, args['-c'], index)
                        else:
                            Interface._print_error("Wrong index")
                    except ValueError:
                        Interface._print_error(
                            "Please enter a positive integer")
            # Deletes a condition
            if args['-d']:
                try:
                    self._t.del_function(cond, args['-d'])
                    Interface._print_info("Condition %s deleted" % args['-d'])
                except KeyError:
                    Interface._print_error(
                        "The condition %s is not in the list" % args['-d'])
                    return
            # Adds a condition
            elif args['-a']:
                # Create the new file if not exists
                if not os.path.isfile(join(self._conds_path, cond, args["-a"] + ".py")):
                    self._create_cond(cond, args["-a"])
                ret = os.system("%s %s.py" % (
                    args["-e"], join(self._conds_path, cond, args["-a"])))
                if ret != 0:
                    Interface._print_error(
                        "The editor is not installed or is not in the PATH")
                    return
                # Save the condition to the Template
                try:
                    self._add_cond(cond, args["-a"])
                except:
                    Interface._print_error(
                        "Bad syntax, please check the code syntax")
                    return
                # If user wants, delete condition from disk
                keepindisk = confirm(
                    'Keep file on disk (%s)? [y/N] ' % join(self._conds_path, cond))
                if not keepindisk:
                    os.remove("%s.py" %
                              join(self._conds_path, cond, args["-a"]))
                Interface._print_info("Condition %s added" % args["-a"])
            # Imports a condition from disk
            elif args['-i']:
                name = args['-i']
                if "/" in name or "\\" in name:
                    if os.path.isfile(name):
                        file = os.path.split(name)[-1]
                        copyfile(name, join(self._conds_path, cond, file))
                        name = file
                if name[-3:] == ".py":
                    name = name[:-3]
                try:
                    self._add_cond(cond, name)
                    Interface._print_info("Condition %s imported" % args['-i'])
                except ModuleNotFoundError:
                    Interface._print_error(
                        "The condition %s is not in disk" % args['-i'])
                    print("(Please place your .py file in correct path)")
                    return

    def _create_cond(self, cond, name):
        """Creates a new condition with the initial source code."""
        code = "def %s(packet):\n\n    # your code here\n\n    # If the condition is meet\n    return packet" % name
        with open("%s.py" % join(self._conds_path, cond, name), 'w') as f:
            f.write(code)

    def _add_cond(self, cond, name):
        """Adds a new condition to the `Template`."""
        m = importlib.import_module(
            "polymorph.conditions.%s.%s" % (cond, name))
        importlib.reload(m)
        self._t.add_function(cond, name, getattr(m, dir(m)[-1]))

    @staticmethod
    def _conditions_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-a": {"type": str,
                       "default": None},
                "-d": {"type": str,
                       "default": None},
                "-e": {"type": str,
                       "default": "pico"},
                "-c": {"type": str,
                       "default": None},
                "-p": {"type": str,
                       "default": None},
                "-s": {"type": bool,
                       "default": False},
                "-i": {"type": str,
                       "default": None},
                "-sa": {"type": bool,
                        "default": False},
                "-sas": {"type": bool,
                         "default": False}}
        # Changing the default editor for Windows OS
        if platform.system() == "Windows":
            opts['-e']['default'] = 'notepad'
        # Return the options
        return opts

    @staticmethod
    def _conditions_help(cond):
        """Builds the help for the conditions commands."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "adds a new condition to the set."),
            ("-d", "deletes a condition from the set."),
            ("-e", "open a text editor that is in the path with the existing conditions, by default pico."),
            ("-c", "select a condition to apply a specific action to it."),
            ("-p", "change the position of a condition."),
            ("-s", "prints the conditions with the source code."),
            ("-i", "import a function from a file."),
            ("-sa", "prints all the conditions on disk."),
            ("-sas", "prints all the conditions source on disk")
        ])
        return OrderedDict([
            ("name", cond),
            ("usage", "%s [-option]" % cond),
            ("description",
             ("Will run when a packet arrive. This functions receive a "
              "parameter that is the packet that will arrive when intercepting"
              " in real time. Furthermore, this functions must return the same"
              " packet if the user want to continue with the execution of the "
              "next conditions. There are three different types of conditions,"
              " Preconditions, which are associated with some input "
              "requirements that the packets must meet, Executions, which will"
              " do processing actions to the previously filtered packets and "
              "Postconditions, which have to be with actions that must be "
              "performed before forwarding the packet (ex. checksum "
              "reclaculations)")),
            ("options", options)
        ])

    def _show(self, command):
        """Pretty print the `Template` fields."""
        if len(command) == 1:
            self._t.show()
            return
        # Parsing the arguments
        cp = CommandParser(TemplateInterface._show_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._show_help())
        # Show a particular layer
        elif args["-l"]:
            self._t.getlayer(args["-l"]).show()

    @staticmethod
    def _show_help():
        """Builds the help for the show command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-l", "shows a particular layer.")
        ])
        return OrderedDict([
            ("name", "show"),
            ("usage", "show [-option]"),
            ("description", "Prints information about the template."),
            ("options", options)
        ])

    @staticmethod
    def _show_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-l": {"type": str,
                       "default": None}}
        return opts

    def _version(self, command):
        """Manages the version of the `Template`."""
        if len(command) == 1:
            print(self._t.version, "\n")
            return
        cp = CommandParser(TemplateInterface._version_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._version_help())
        # Add a new version
        elif args["-n"]:
            self._t.version = args["-n"]
            Interface._print_info("New version %s added" % args["-n"])

    @staticmethod
    def _version_help():
        """Builds the help for the version command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-n", "sets a new version.")
        ])
        return OrderedDict([
            ("name", "version"),
            ("usage", "version [-option]"),
            ("description", "Manages the version of the Template."),
            ("options", options)
        ])

    @staticmethod
    def _version_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-n": {"type": str,
                       "default": None}}
        return opts

    def _description(self, command):
        """Manages the description of the `Template`."""
        if len(command) == 1:
            print(self._t.description, "\n")
            return
        # Parsing arguments
        cp = CommandParser(TemplateInterface._description_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._description_help())
        # Adding a new description
        elif args["-n"]:
            self._t.description = args["-n"]
            Interface._print_info("New description added")

    @staticmethod
    def _description_help():
        """Builds the help for the description command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-n", "sets a new description.")
        ])
        return OrderedDict([
            ("name", "description"),
            ("usage", "description [-option]"),
            ("description", "Manages the description of the Template."),
            ("options", options)
        ])

    @staticmethod
    def _description_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-n": {"type": str,
                       "default": None}}
        return opts

    def _save(self, command):
        """Saves the `Template` to disk."""
        if len(command) == 1:
            path = input("Introduce the path and the file name: ")
            try:
                self._t.write(path)
                Interface._print_info("Template saved to disk")
            except:
                Interface._print_error("The path %s does not exist" % path)
            return
        # Parsing arguments
        cp = CommandParser(TemplateInterface._save_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._save_help())
        # Write to a specific path
        elif args["-p"]:
            try:
                self._t.write(args['-p'])
                Interface._print_info("Template saved to disk")
            except:
                Interface._print_error(
                    "The path %s does not exist" % args['-p'])

    @staticmethod
    def _save_help():
        """Builds the help for the save command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-p", "path where the Template will be written.")
        ])
        return OrderedDict([
            ("name", "save"),
            ("usage", "save [-option]"),
            ("description", "Saves the Template to disk."),
            ("options", options)
        ])

    @staticmethod
    def _save_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-p": {"type": str,
                       "default": None}}
        return opts

    def _layer(self, command):
        """Manages the access to a `TLayer` of the `Template`."""
        if len(command) == 1:
            Interface.print_help(TemplateInterface._layer_help())
        elif len(command) == 2 and command[1].upper() in self._t.layernames():
            li = LayerInterface(self._t.getlayer(
                command[1].upper()), self._index, self._poisoner)
            li.run()
        else:
            cp = CommandParser(TemplateInterface._layer_opts())
            args = cp.parse(command)
            if not args:
                Interface._argument_error()
                return
            # Print the help
            if args["-h"]:
                Interface.print_help(TemplateInterface._layer_help())
            # Adds a new layer
            elif args["-a"]:
                hexdump.hexdump(self._t.raw)
                print()
                start = input("Start byte of the custom layer: ")
                end = input("End byte of the custom layer: ")
                if start.isdecimal() and end.isdecimal():
                    lslice = str(slice(int(start), int(end))).encode().hex()
                    new_layer = TLayer(args["-a"], raw=self._t.raw.hex(),
                                       lslice=lslice, custom=True)
                    self._t.addlayer(new_layer)
                    Interface._print_info(
                        "New layer %s added to the Template" % args["-a"])
                else:
                    Interface._print_error(
                        "The start or end byte is not a number")
            # Deletes an existing layer
            elif args["-d"]:
                del_layer = self._t.getlayer(args["-d"])
                if del_layer:
                    self._t.dellayer(del_layer)
                    Interface._print_info("Layer %s deleted" % args["-d"])
                else:
                    Interface._print_error(
                        "The layer %s does not exist" % args["-d"])

    @staticmethod
    def _layer_help():
        """Builds the help for the layer command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-a", "adds a new layer to the Template."),
            ("-d", "deletes a custom layer from the Template.")
        ])
        return OrderedDict([
            ("name", "layer"),
            ("usage", "layer <name> [-option]"),
            ("description", "access and manage the layers of the Template."),
            ("options", options)
        ])

    @staticmethod
    def _layer_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-a": {"type": str,
                       "default": None},
                "-d": {"type": str,
                       "default": None}}
        return opts

    def _intercept(self, command):
        """Starts intercepting packets between two machines"""
        if len(command) == 1:
            i = Interceptor(self._t)
            i.intercept()
            return
        # Parsing arguments
        cp = CommandParser(TemplateInterface._intercept_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._intercept_help())
        # Adds a new iptables rule
        elif args["-ipt"] or args["-ip6t"]:
            i = Interceptor(self._t, iptables_rule=args["-ipt"],
                            ip6tables_rule=args["-ip6t"])
            i.intercept()

    @staticmethod
    def _intercept_help():
        """Builds the help for the intercept command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-ipt", "iptables rule for ipv4"),
            ("-ip6t", "iptables rule for ipv6")
        ])
        return OrderedDict([
            ("name", "intercept"),
            ("usage", "intercept <template> [-option]"),
            ("description", "Starts intercepting packets in real time."),
            ("options", options)
        ])

    @staticmethod
    def _intercept_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-ipt": {"type": str,
                         "default": "iptables -A FORWARD -j NFQUEUE --queue-num 1"},
                "-ip6t": {"type": str,
                          "default": "ip6tables -A FORWARD -j NFQUEUE --queue-num 1"}}
        return opts

    def _layers(self, command):
        """Shows the layers of the `Template`."""
        if len(command) == 1:
            print(colored("\n".join(self._t.layernames()), 'cyan'), "\n")
            return
        cp = CommandParser(TemplateInterface._layers_opts())
        args = cp.parse(command)
        if not args:
            Interface._argument_error()
            return
        # Print the help
        if args["-h"]:
            Interface.print_help(TemplateInterface._layers_help())
        # Prints the custom layers (layers added by the user)
        elif args["-c"]:
            clayers = [l.name for l in self._t.customlayers()]
            print(colored("\n".join(clayers), 'cyan'), "\n")

    @staticmethod
    def _layers_help():
        """Builds the help for the layers command."""
        options = OrderedDict([
            ("-h", "prints the help."),
            ("-c", "prints the custom layers.")
        ])
        return OrderedDict([
            ("name", "layers"),
            ("usage", "layers [-option]"),
            ("description", "Prints the layers of the Template."),
            ("options", options)
        ])

    @staticmethod
    def _layers_opts():
        """Returns command options in a form that can be handled by the
        command parser."""
        opts = {"-h": {"type": bool,
                       "default": False},
                "-c": {"type": bool,
                       "default": False}}
        return opts
