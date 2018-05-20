#! /usr/bin/env python3

# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph
from polymorph.utils import pkt_to_template, get_arpspoofer, set_ip_forwarding
from polymorph.interceptor import Interceptor
from scapy.sendrecv import sniff
from termcolor import colored
import os
import polymorph
from shutil import copyfile
import importlib


class Cli(object):

    def __init__(self):
        """Initialization method of the Cli class."""
        self._proto = None
        self._fields = None
        self._in_pkt = None
        self._types = None
        self._template = None
        self._layer = None
        self._values = None
        self._byte = None
        self._show_pkts = False
        self._recalculate = False
        self.poisoner = None
        self._conds_path = os.path.dirname(polymorph.conditions.__file__)

    @staticmethod
    def print_info(text):
        print("[" + colored("INFO", 'blue', attrs=['bold']) + "]", text)

    @staticmethod
    def print_ok(text):
        print("[" + colored("OK", 'green', attrs=['bold']) + "]", text)

    @staticmethod
    def print_error(text):
        print("[" + colored("ERROR", 'red', attrs=['bold']) + "]", text)

    def run_template(self, template, ipt, ip6t):
        """Runs a `Template`.

        Parameters
        ----------
        template: :obj:`Template`
            Template to intercept in real time.
        ipt: :obj:`str`
            Iptables version 4 rule.
        ip6t: :obj:`str`
            Iptables version 6 rule.

        """
        interceptor = Interceptor(template, ipt, ip6t)
        interceptor.intercept()

    def _get_patterns(self, chain, pattern_types):
        """ Split a chain into patterns and transform them to their
        corresponding type.

        Parameters
        ----------
        chain : :obj:`str`
            Chain that contains the patterns.
        pattern_types: :obj:`list`
            List of types to apply to the extracted patterns.

        Returns
        -------
        patterns : :obj:`list`
            List of the extracted patterns with their corresponding type.

        """
        patterns = chain.split(";")
        # Casting the patterns with the types
        for i in range(len(patterns)):
            if len(pattern_types) <= i:
                break
            if pattern_types[i] == "int":
                patterns[i] = int(patterns[i])
            elif pattern_types[i] == "bytes":
                patterns[i] = patterns[i].encode()
        return patterns

    def set_spoofer(self, s_type, target, gateway, iface):
        """Sets a spoofer.

        Parameters
        ----------
        s_type: :obj:`str`
            Type of the spoofer.
        target: :obj:`str`
            Target of the spoofer.
        gateway: :obj:`str`
            Gateway of the spoofer.
        iface: :obj:`str`
            Network interface.

        """
        if s_type in [None, "ARP", "arp"]:
            # Set ip forwarding in Linux Operating systems
            set_ip_forwarding(1)
            try:
                # Getting the poisoner
                self.poisoner = get_arpspoofer(target.replace(";", ","), gateway, iface)
                self.poisoner.start()
                Cli.print_ok(
                    "ARP spoofing started between %s and %s" % (gateway, target))
            except:
                Cli.print_error("Invalid target(s) or gateway")
                set_ip_forwarding(0)
        else:
            Cli.print_error("%s it is not an accepted type of spoofing." % s_type)

    def show_fields(self, proto, in_pkt, types, fields, showpkts=False):
        """Handles the show fields options.

        Notes
        -----
        This function will perform a sniffing process until it captures a
        packet that implements the protocol selected by the user. Once
        captured, it will dissect this packet in real time and show its fields.

        Parameters
        ----------
        proto : :obj:`str`
            Protocol that implements the packet that the user wants to show.
        in_pkt : :obj:`str`, optional
            Patterns that allow filtering packets by their content. By default
            the pattern is interpreted as string.
        types : :obj:`str`, optional
            Interprets the in_pkt patterns in different formats (str, int, bytes, hex).
        fields : :obj:`str`
            Allows the user to filter the packets by the fields they contain.

        """
        self._types = types.split(";") if types else []
        self._proto = proto.upper()
        self._in_pkt = self._get_patterns(in_pkt, self._types) if in_pkt else []
        self._fields = fields.split(";") if fields else []
        self._show_pkts = True if showpkts else False

        # Printing information about the process
        Cli.print_info("Waiting for a network packet which implements the %s "
                       "protocol" % self._proto)
        Cli.print_info("The packet will be dissected to show its fields")
        # Starting the sniffing process
        try:
            Cli.print_ok("Sniffing process started. Waiting for packets...")
            sniff(prn=self._print_fields)
        except KeyboardInterrupt:
            pass

    def _print_fields(self, packet):
        """Hook function that is used when Scapy sniffs any packet.

        Parameters
        ----------
        packet : :obj:`scapy_pkt`
            Packet in Scapy format that is sniffed in real time.

        """

        def pattern_match(raw):
            """Check if the patterns inserted by the user are in the network
            packet. The comparison process is done in hexadecimal."""
            raw = raw.hex()
            for pattern in self._in_pkt:
                if type(pattern) is int:
                    pattern = format(pattern, 'x')
                else:
                    pattern = pattern.encode().hex()
                if pattern not in raw:
                    return False
            return True

        def fields_match(t, layer):
            """Check if the field is found in the template."""
            for field in self._fields:
                if not t.getlayer(layer).isfield(field):
                    return False
            return True

        def print_layer(t, proto):
            """Prints the `Template` layer with all its fields.

            Parameters
            ----------
            t: :obj:`Template`
                Template generated from the Scapy packet.
            proto: :obj:`str`
                Protocol of the layer that the user wants to print.

            """
            if not fields_match(t, proto):
                return
            Cli.print_ok("Packet captured. Printing the fields...")
            if self._show_pkts:
                template.show()
            else:
                template.getlayer(proto).show()
            raise KeyboardInterrupt

        # There is a lot of tcp traffic that slows down the process,
        # so the packets are filtered before generating the template
        if packet.lastlayer().name == "TCP" and self._proto != "TCP":
            return
        # Return if the packet not match the patterns
        if not pattern_match(bytes(packet)):
            return
        # Generation of the template
        template = pkt_to_template(packet)
        # The names of the layers may contain the word RAW if Polymorph had
        # to use advanced dissectors on the raw layer that Scapy could not dissect
        if template.islayer(self._proto):
            print_layer(template, self._proto)
        elif template.islayer("RAW." + self._proto):
            print_layer(template, "RAW." + self._proto)

    def insert_values(self, proto, fields, values, types, in_pkt, ipt, ip6t, count,
                      byte, precs, execs, posts, rec):
        """Handles the insert values options.

        Notes
        -----
        This function will perform a sniffing process until it captures a
        packet that implements the protocol selected by the user. Once
        captured, it will transform that packet into a Template. The tool
        will use the Template for intercepting packets in real time.

        Parameters
        ----------
        proto : :obj:`str`
            Protocol that implements the packet that the user wants to show.
        in_pkt : :obj:`str`, optional
            Patterns that allow filtering packets by their content. By default
            the pattern is interpreted as string.
        types : :obj:`str`, optional
            Interprets the in_pkt patterns in different formats (str, int, bytes, hex).
        fields : :obj:`str`
            Allows the user to filter the packets by the fields they contain.
        values : :obj:`str`
            Values to insert into the intercepted packet in real time.
        ipt : :obj:`str`
            Iptables rule for intercepting in real time.
        ip6t : :obj:`str`
            Ip6tables rule for intercepting in real time.
        count : int
            Number of packets in which the user want to insert the values.
        byte : :obj:`bytes`
            If the packet is in byte insert mode.
        precs : :obj:`str`
            Path to some preconditions.
        posts : :obj:`str`
            Path to some postconditions.
        execs : :obj:`str`
            Path to some executions.
        rec : bool
            If a field must be recalculated.

        """
        self._types = types.split(";") if types else []
        self._proto = proto.upper()
        self._in_pkt = self._get_patterns(in_pkt, self._types) if in_pkt else []
        self._fields = fields.split(";") if fields else []
        self._byte = byte.split(";") if byte else None
        self._values = self._get_patterns(values, self._types) if values else []
        self._recalculate = True if rec else False

        # Printing the information about the process
        Cli.print_info("Polymorph needs to capture a packet like the one you "
                       "want to modify in real time to learn how it is.")
        Cli.print_info("It will be in sniffing mode until you generate the packet")
        Cli.print_ok("Sniffing mode started. Waiting for packets...")
        # Sniffing of the packets
        try:
            sniff(prn=self._gen_template)
        except KeyboardInterrupt:
            pass
        if not self._template:
            Cli.print_error("The template has not been generated.")
            return
        # Sniffing mode finished. Polymorph has the Template.
        Cli.print_info("Great! Polymorph has the structure of the packet! "
                       "Let's start breaking things!")
        Cli.print_ok("Process of interception and modification of packets in real time started.")
        # Adding the preconditions, executions and postconditions to the template
        if execs:
            self._get_conds("executions", execs)
        else:
            if byte:
                self._template.add_execution('exec', Cli.execution2)
            else:
                self._template.add_execution('exec', Cli.execution)
        if posts:
            self._get_conds("postconditions", posts)
        else:
            if self._template.islayer("IPV6"):
                self._template.add_postcondition('post', Cli.postcondition2)
            else:
                self._template.add_postcondition('post', Cli.postcondition)
        if precs:
            self._get_conds("preconditions", precs)
        else:
            self._template.add_precondition('prec', Cli.precondition)
        # Retrieving the fields and insert values
        if byte:
            insert_values = {self._byte[i]: self._values[i]
                             for i in range(len(self._byte))}
        else:
            insert_values = {self._fields[i]: self._values[i]
                             for i in range(len(self._fields))}
        # Initialization of the interceptor and global variables
        interceptor = Interceptor(self._template, ipt, ip6t)
        setattr(interceptor.packet, 'insert_values', insert_values)
        setattr(interceptor.packet, 'insert_layer', self._layer)
        setattr(interceptor.packet, 'in_pkt', self._in_pkt)
        setattr(interceptor.packet, 'insert_times', 1)
        setattr(interceptor.packet, 'count', count)
        interceptor.intercept()

    def _gen_template(self, packet):
        """Hook function that is used when Scapy sniffs any packet.

        Parameters
        ----------
        packet : :obj:`scapy_pkt`
            Packet in Scapy format that is sniffed in real time.

        """

        def pattern_match(raw):
            """Check if the patterns inserted by the user are in the network
            packet. The comparison process is done in hexadecimal."""
            raw = raw.hex()
            for pattern in self._in_pkt:
                if type(pattern) is int:
                    pattern = format(pattern, 'x')
                else:
                    pattern = pattern.encode().hex()
                if pattern not in raw:
                    return False
            return True

        def fields_match(t, layer):
            """Check if the field is found in the template."""
            for field in self._fields:
                if not t.getlayer(layer).isfield(field):
                    return False
            return True

        # There is a lot of tcp traffic that slows down the process,
        # so the packets are filtered before generating the template
        if packet.lastlayer().name == "TCP" and self._proto != "TCP":
            return
        # Return if the packet not match the patterns
        if not pattern_match(bytes(packet)):
            return
        # Generation of the template
        template = pkt_to_template(packet)
        # The names of the layers may contain the word RAW if Polymorph had
        # to use advanced dissectors on the raw field that Scapy could not dissect
        if template.islayer(self._proto):
            if fields_match(template, self._proto):
                self._template = template
                self._layer = self._proto
                if self._recalculate:
                    self.add_recalculate()
                raise KeyboardInterrupt
        elif template.islayer("RAW." + self._proto):
            if fields_match(template, "RAW." + self._proto):
                self._template = template
                self._layer = "RAW." + self._proto
                if self._recalculate:
                    self.add_recalculate()
                raise KeyboardInterrupt

    def _get_conds(self, cond, paths):
        """This function imports the preconditions, postconditions and executions from
        any path."""
        paths = paths.split(";")
        for p in paths:
            if os.path.isfile(p):
                file = os.path.split(p)[-1]
                copyfile(p, os.path.join(self._conds_path, cond, file))
                m = importlib.import_module("polymorph.conditions.%s.%s" % (cond, file[:-3]))
                importlib.reload(m)
                self._template.add_function(cond, file[:-3], getattr(m, dir(m)[-1]))
            else:
                Cli.print_error("The file %s does not exist" % p)

    def add_recalculate(self):
        """Adds a structu to the `Template`."""

        def add_struct(rec_f, st_b, expr):
            fields = Cli._extrac_deps(st_b, expr)
            if fields:
                try:
                    self._template[self._layer].add_struct(rec_f, fields, st_b, expr)
                    Cli.print_ok("Struct added to field %s." % rec_f)
                except:
                    Cli.print_error(
                        "Wrong fields or wrong syntax referring to the fields.")
                    return
            else:
                Cli.print_error(
                    "Wrong syntax for referring to the fields. Please use 'this.field' syntax.")

        print("\n[" + colored("RECALCULATE", 'green', attrs=['bold']) + "]")
        Cli.print_info("Polymorph needs some information to recalculate a field in real time.")
        Cli.print_info("If you reference a field in the packet to calculate the start byte or the "
                       "expression, use the syntax 'this.field'")
        print()
        while True:
            interrog = colored("Q", 'red', attrs=['bold'])
            rec_field = input("[" + interrog + "] Field to recalculate?: ")
            st_byte = input("[" + interrog + "] Start byte?: ")
            expression = input("[" + interrog + "] Expression that provides its length?: ")
            add_struct(rec_field, st_byte, expression)
            q = input("[" + interrog + "] Do you want to recalculate another field [y/N]?: ")
            print()
            if q not in ["y", "Y"]:
                break

    @staticmethod
    def _extrac_deps(start_byte, expression):
        """Extracts the field from the recalculate input values."""
        patterns = start_byte.split(" ") + expression.split(" ")
        fields = []
        for p in patterns:
            if 'this.' in p and p[5:] not in fields:
                fields.append(p[5:])
        return fields

    # -----------------------------------------
    # PRECONDITIONS, EXECUTIONS, POSTCONDITIONS
    # -----------------------------------------
    @staticmethod
    def precondition(packet):
        if packet.count and packet.insert_times > packet.count:
            return None
        raw = packet.raw.hex()
        for pattern in packet.in_pkt:
            if type(pattern) is int:
                pattern = format(pattern, 'x')
            else:
                pattern = pattern.encode().hex()
            if pattern not in raw:
                return None
        return packet

    @staticmethod
    def execution(packet):
        packet.insert_times += 1
        layer = packet.insert_layer
        for field, value in packet.insert_values.items():
            packet[layer][field] = value
        return packet

    @staticmethod
    def execution2(packet):
        packet.insert_times += 1
        for field, value in packet.insert_values.items():
            f = field.split(":")
            packet.insert(int(f[0].strip('\\')),
                          int(f[1].strip('\\')),
                          value.encode())
        return packet

    @staticmethod
    def postcondition(packet):
        from scapy.all import IP
        pkt = IP(packet.get_payload())
        if pkt.haslayer('IP'):
            del pkt['IP'].chksum
            del pkt['IP'].len
        if pkt.haslayer('TCP'):
            del pkt['TCP'].chksum
        if pkt.haslayer('ICMP'):
            del pkt['ICMP'].chksum
        pkt.show2()
        packet.raw = bytes(pkt)
        return packet

    @staticmethod
    def postcondition2(packet):
        from scapy.all import IPv6
        pkt = IPv6(packet.get_payload())
        if pkt.haslayer('IPv6'):
            del pkt['IPv6'].plen
        if pkt.haslayer('TCP'):
            del pkt['TCP'].chksum
        if pkt.haslayer('ICMP'):
            del pkt['ICMP'].chksum
        pkt.show2()
        packet.raw = bytes(pkt)
        return packet
