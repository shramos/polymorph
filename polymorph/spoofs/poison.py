# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from scapy.all import get_if_addr, get_if_hwaddr, get_working_if

class Poison(object):
    def __init__(self, targets, gateway, gatewaymac=None, ignore=None,
                 arpmode='rep', iface=None, mac=None, ip=None):
        self._iface = iface
        if not iface:
            self._iface = self.get_iface()
        self._ip = ip
        if not ip:
            self._ip = self.get_ip()
        self._mac = mac
        if not mac:
            self._mac = self.get_mac()
        self._arpmode = arpmode  
        self._targets = targets
        self._ignore = ignore
        self._gateway = gateway
        self._gatewaymac = gatewaymac

    @property
    def arpmode(self):
        return self._arpmode

    @property
    def ip(self):
        return self._ip

    @property
    def targets(self):
        return self._targets

    @property
    def ignore(self):
        return self._ignore

    @property
    def mac(self):
        return self._mac

    @property
    def interface(self):
        return self._iface

    @property
    def gateway(self):
        return self._gateway

    @property
    def gatewaymac(self):
        return self._gatewaymac

    def get_mac(self):
        try:
            mac_address = get_if_hwaddr(self._iface)
            return mac_address
        except Exception as e:
            print("Error retrieving MAC address from {}: {}".format(self._iface, e))

    def get_ip(self):
        try:
            ip_address = get_if_addr(self._iface)
            if (ip_address == "0.0.0.0") or (ip_address is None):
                print("Interface {} does not have an assigned IP address".format(self._iface))
            return ip_address
        except Exception as e:
            print("Error retrieving IP address from {}: {}".format(self._iface, e))

    def get_iface(self):
        iface = get_working_if()
        return iface
