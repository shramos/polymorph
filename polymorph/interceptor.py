# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from polymorph.packet import Packet
import platform
import subprocess


class Interceptor(object):
    """This is the class responsible for intercepting packages in rela time,
    interpreting these packets, interpreting the preconditions, executions
    and post-conditions of the template and forwarding the modified package
    to the target machine."""

    def __init__(self, template,
                 iptables_rule="iptables -A FORWARD -j NFQUEUE --queue-num 1",
                 ip6tables_rule="ip6tables -A FORWARD -j NFQUEUE --queue-num 1"):
        """Initialization method of the `Interceptor` class.

        Parameters
        ----------
        template : :obj:`Template`
            A `Template` objet that will be parsed to obtain the conditions
            and other values.
        iptables_rule : :obj:`str`
            Iptables rule for intercepting packets.
        ip6tables_rule : :obj:`str`
            Iptables rule for intercepting packets for ipv6.

        """
        self.iptables_rule = iptables_rule
        self.ip6tables_rule = ip6tables_rule
        self.packet = Packet(template)
        self._preconditions = [template.get_precondition(pc)
                               for pc in template.precondition_names()]
        self._executions = [template.get_execution(ex)
                            for ex in template.execution_names()]
        self._postconditions = [template.get_postcondition(pr)
                                for pr in template.postcondition_names()]
        self._functions = [self._preconditions,
                           self._executions,
                           self._postconditions]

    def set_iptables_rules(self):
        subprocess.check_output(self.iptables_rule, shell=True, stderr=subprocess.STDOUT)
        subprocess.check_output(self.ip6tables_rule, shell=True, stderr=subprocess.STDOUT)

    def clean_iptables(self):
        subprocess.check_output("iptables -F", shell=True, stderr=subprocess.STDOUT)
        subprocess.check_output("ip6tables -F", shell=True, stderr=subprocess.STDOUT)

    def linux_modify(self, packet):
        """This is the callback method that will be called when a packet
        is intercepted. It is responsible of executing the preconditions,
        executions and postconditions of the `Template`.

        Parameters
        ----------
        packet : :obj:`Packet`
            Netfilterqueue packet object. The packet that is intercepted.

        """
        # Initialization of the Packet with the new raw bytes
        self.packet.raw = packet.get_payload()
        # Executing the preconditions, executions and postconditions
        for functions in self._functions:
            for condition in functions:
                pkt = condition(self.packet)
                # If the condition returns None, it is not held and the
                # packet must be forwarded
                if not pkt:
                    if self.packet:
                        packet.set_payload(self.packet.raw)
                    packet.accept()
                    return
                # If the precondition returns the packet, we assign it to the
                # actual packet
                self.packet = pkt
        # If all the conditions are met, we assign the payload of the modified
        # packet to the nfqueue packet and forward it
        packet.set_payload(self.packet.raw)
        packet.accept()

    def windows_modify(self, packet, w, pydivert):
        """This is the callback method that will be called when a packet
        is intercepted. It is responsible of executing the preconditions,
        executions and postconditions of the `Template`.

        Parameters
        ----------
        packet : :obj:`Packet`
            Netfilterqueue packet object. The packet that is intercepted.
        w : pointer
            windiver pointer.

        """
        # Initialization of the Packet with the new raw bytes
        self.packet.raw = packet.raw.tobytes()
        # Executing the preconditions, executions and postconditions
        for functions in self._functions:
            for condition in functions:
                pkt = condition(self.packet)
                # If the condition returns None, it is not held and the
                # packet must be forwarded
                if not pkt:
                    w.send(packet)
                    return
                # If the precondition returns the packet, we assign it to the
                # actual packet
                self.packet = pkt
        # If all the conditions are met, we assign the payload of the modified
        # packet to the nfqueue packet and forward it
        packet = pydivert.Packet(self.packet.raw, packet.interface, packet.direction)
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
