# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.packet import Packet
import platform
import subprocess
from scapy.all import IP, IPv6
import struct
import socket
import ipaddress


class Interceptor(object):
    """This is the class responsible for intercepting packets in real time,
    interpreting these packets, interpreting the custom functions of the
    template and forwarding the modified packet to the target machine."""

    def __init__(self, template,
                 iptables_rule="iptables -A FORWARD -j NFQUEUE --queue-num 1",
                 ip6tables_rule="ip6tables -A FORWARD -j NFQUEUE --queue-num 1"):
        """Initialization method of the `Interceptor` class.

        Parameters
        ----------
        template : :obj:`Template`
            A `Template` objet that will be parsed to obtain the custom functions
            and other values.
        iptables_rule : :obj:`str`
            Iptables rule for intercepting packets.
        ip6tables_rule : :obj:`str`
            Iptables rule for intercepting packets for ipv6.

        """
        self.iptables_rule = iptables_rule
        self.ip6tables_rule = ip6tables_rule
        self.packet = Packet(template)
        self._functions = [template.get_function(func_name)
                           for func_name in template.function_names()]

    def set_iptables_rules(self):
        subprocess.check_output(
            self.iptables_rule, shell=True, stderr=subprocess.STDOUT)
        subprocess.check_output(self.ip6tables_rule,
                                shell=True, stderr=subprocess.STDOUT)

    def clean_iptables(self):
        subprocess.check_output(
            "iptables -F", shell=True, stderr=subprocess.STDOUT)
        subprocess.check_output(
            "ip6tables -F", shell=True, stderr=subprocess.STDOUT)

    def linux_modify(self, packet):
        """This is the callback method that will be called when a packet
        is intercepted. It is responsible of executing the custom functions
        of the `Template`.

        Parameters
        ----------
        packet : :obj:`Packet`
            Netfilterqueue packet object. The packet that is intercepted.

        """
        # Initialization of the Packet with the new raw bytes
        self.packet.raw = packet.get_payload()
        # Executing the cutom functions
        for function in self._functions:
            pkt = function(self.packet)
            # If the function returns None, it is not held and the
            # packet must be forwarded
            if not pkt:
                if self.packet:
                    packet.set_payload(self.packet.raw)
                packet.accept()
                return
            # if the drop flag is activated, the network packet is dropped
            if pkt.drop:
                packet.drop()
                return
            # If the function returns the packet, we assign it to the
            # actual packet
            self.packet = pkt
        # If all the functions are met, we assign the payload of the modified
        # packet to the nfqueue packet and forward it
        # Before sending the packet, we recalculate the chksums fields
        if self.packet.rec_chksums:
            self.packet = self._rec_chksums(self.packet)
        packet.set_payload(self.packet.raw)
        packet.accept()

    def windows_modify(self, packet, w, pydivert):
        """This is the callback method that will be called when a packet
        is intercepted. It is responsible of executing the custom functions
        of the `Template`.

        Parameters
        ----------
        packet : :obj:`Packet`
            Netfilterqueue packet object. The packet that is intercepted.
        w : pointer
            windiver pointer.

        """
        # Initialization of the Packet with the new raw bytes
        self.packet.raw = packet.raw.tobytes()
        # Executing the custom functions
        for function in self._functions:
            pkt = function(self.packet)
            # If the function returns None, it is not held and the
            # packet must be forwarded
            if not pkt:
                w.send(packet)
                return
            # if the drop flag is activated, the network packet is dropped
            if pkt.drop:
                return
            # If the function returns the packet, we assign it to the
            # actual packet
            self.packet = pkt
        # If all the functions are met, we assign the payload of the modified
        # packet to the pydivert packet and forward it
        # Before sending the packet, we recalculate the chksums fields
        if self.packet.rec_chksums:
            self.packet = self._rec_chksums(self.packet)
        packet = pydivert.Packet(
            self.packet.raw, packet.interface, packet.direction)
        w.send(packet)

    def intercept(self):
        """This method intercepts the packets and send them to a callback
        function."""
        # For Windows Platforms
        if platform.system() == "Windows":
            import pydivert
            w = pydivert.WinDivert()
            w.open()
            print("[*] Waiting for packets...\n\n(Press Ctrl-C to exit)\n")
            try:
                while True:
                    self.windows_modify(w.recv(), w, pydivert)
            except KeyboardInterrupt:
                w.close()
        # For Linux platforms
        elif platform.system() == "Linux":
            from netfilterqueue import NetfilterQueue
            nfqueue = NetfilterQueue()
            # The iptables rule queue number by default is 1
            nfqueue.bind(1, self.linux_modify)
            try:
                self.set_iptables_rules()
                print("[*] Waiting for packets...\n\n(Press Ctrl-C to exit)\n")
                nfqueue.run()
            except KeyboardInterrupt:
                self.clean_iptables()
        else:
            print("Sorry. Platform not supported!\n")

    def _rec_chksums(self, packet):
        """Auxiliary function that makes it easy to recalculate the control fields
        of some common layers."""

        def chksum(packet):
            if len(packet) % 2 != 0:
                packet += b'\0'
            res = sum(array.array("H", packet))
            res = (res >> 16) + (res & 0xffff)
            res += res >> 16
            ck = (~res) & 0xffff
            return struct.pack("H", ck).hex()

        pkt_layers = list(packet._layers)

        # Calculation of checksums for different layers on IPv4
        if "IP" in pkt_layers and packet["IP"]["version"] == 4:

            # Handling the IPv4 checksum
            packet["IP"]["checksum"] = '0x0000'
            lstart = packet['IP'].slice.start - 14
            lend = lstart + 20
            ck = chksum(packet.raw[lstart:lend])
            packet["IP"]["checksum"] = ck

            # Handling TCP over IPv4
            if "TCP" in pkt_layers and packet["IP"]["proto"] == 6:
                # We build a false IP header
                fake_hdr = struct.pack(
                    '!4s4sHH',
                    socket.inet_aton(packet["IP"]["src"]),
                    socket.inet_aton(packet["IP"]["addr"]),
                    6,
                    len(packet["TCP"]))
                packet["TCP"]["checksum"] = '0x0000'
                ck = chksum(
                    fake_hdr + packet.raw[packet['TCP'].slice.start - 14:])
                packet["TCP"]["checksum"] = ck
                return packet

            # Handling ICMP over IPv4
            elif 'ICMP' in pkt_layers and packet["IP"]["proto"] == 1:
                packet["ICMP"]["checksum"] = '0x0000'
                ck = chksum(packet.raw[packet['ICMP'].slice.start - 14:])
                packet["ICMP"]["checksum"] = ck
                return packet

            # Handling UDP over IPv4
            elif 'UDP' in pkt_layers and packet["IP"]["proto"] == 17:
                # We build a false IP header
                fake_hdr = struct.pack(
                    '!4s4sHH',
                    socket.inet_aton(packet["IP"]["src"]),
                    socket.inet_aton(packet["IP"]["addr"]),
                    17,
                    len(packet["UDP"]))
                packet["UDP"]["checksum"] = '0x0000'
                ck = chksum(
                    fake_hdr + packet.raw[packet['UDP'].slice.start - 14:])
                packet["UDP"]["checksum"] = ck
                return packet

        # Calculation of checksums for different layers on IPv6
        elif 'IPV6' in pkt_layers and packet["IPV6"]["version"] == 6:

            # Handling TCP over IPv6
            if "TCP" in pkt_layers and packet["IPV6"]["nxt"] == 6:
                # We build a false IPV6 fake header
                fake_hdr = struct.pack(
                    '!16s16sHH',
                    ipaddress.IPv6Address(packet["IPV6"]["src"]).packed,
                    ipaddress.IPv6Address(packet["IPV6"]["addr"]).packed,
                    6,
                    len(packet["TCP"]))
                packet["TCP"]["checksum"] = '0x0000'
                ck = chksum(
                    fake_hdr + packet.raw[packet['TCP'].slice.start - 14:])
                packet["TCP"]["checksum"] = ck
                return packet

            # Handling ICMPV6 over IPv6
            elif 'ICMPV6' in pkt_layers and packet["IPV6"]["nxt"] == 58:
                # We build a false IPV6 header
                fake_hdr = struct.pack(
                    '!16s16sHH',
                    ipaddress.IPv6Address(packet["IPV6"]["src"]).packed,
                    ipaddress.IPv6Address(packet["IPV6"]["addr"]).packed,
                    58,
                    len(packet["ICMPV6"]))
                packet["ICMPV6"]["checksum"] = '0x0000'
                ck = chksum(
                    fake_hdr + packet.raw[packet['ICMPV6'].slice.start - 14:])
                packet["ICMPV6"]["checksum"] = ck
                return packet

            # Handling UDP over IPv6
            elif 'UDP' in pkt_layers and packet["IPV6"]["nxt"] == 17:
                # We build a false IPV6 header
                fake_hdr = struct.pack(
                    '!16s16sHH',
                    ipaddress.IPv6Address(packet["IPV6"]["src"]).packed,
                    ipaddress.IPv6Address(packet["IPV6"]["addr"]).packed,
                    17,
                    len(packet["UDP"]))
                packet["UDP"]["checksum"] = '0x0000'
                ck = chksum(
                    fake_hdr + packet.raw[packet['UDP'].slice.start - 14:])
                packet["UDP"]["checksum"] = ck
                return packet

        # If no condition is met we return the original package
        return packet
