# File from polymorph project
# Copyright (C) 2020 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from scapy.sendrecv import sniff
from scapy.utils import wrpcap
from polymorph.tgenerator import TGenerator
from polymorph.tlist import TList
from polymorph.template import Template
from polymorph.spoofs.arpspoof import ARPpoisoner
from polymorph.spoofs.poison import Poison
from polymorph.interceptor import Interceptor
import platform
import polymorph
from os.path import dirname, join

POLYM_PATH = dirname(polymorph.__file__)


def capture(userfilter=None, pcapname=".tmp.pcap", func=None, count=0, time=None):
    """This function is a wrapper function above the sniff scapy function. The
    result is a list of templates. 

    Parameters
    ----------
    userfilter : :obj:`str`
        Filters to capture packets in Wireshark format.
    pcapname : :obj:`str`
        Path where the pcap will be written.
    func : :obj:`function`
        Function to be called when a packet arrive, the packet will be passed
        as parameter.
    count : int
        Number of packets to capture.
    time : int
        Stop sniffing after a given time.

    Returns
    -------
    :obj:`TList`
        List of templates

    """
    # We manually obtain the available network interfaces
    if platform.system() == "Linux":
        interfaces = os.listdir('/sys/class/net/')
    else:
        interfaces = None
    if func:
        plist = sniff(prn=func, count=count, timeout=time, iface=interfaces)
    else:
        plist = sniff(count=count, timeout=time, iface=interfaces)
    # Save the list of packets to disk for later reading with Pyshark
    if len(plist) > 0:
        pcap_path = join(POLYM_PATH, pcapname)
        wrpcap(pcap_path, plist)
        tgen = TGenerator(pcap_path, userfilter)
        # Returns a list of `Template` objects
        tlist = TList(tgen, pcap_path)
        return tlist
    return None


def readpcap(pcapfile, userfilter=None):
    """This function is a wrapper function above the generate function from
    `TGenerator` class. The result is a `TList` object.

    Parameters
    ----------
    pcapfile : :obj:`str`
        Path to a pcap file.

    Returns
    -------
    :obj: `TList`
        List of templates.

    """
    tgen = TGenerator(pcapfile, userfilter=userfilter)
    return TList(tgen, pcap_path=pcapfile)


def readtemplate(path):
    """This function reads a template from disk and returns its
    representation.

    Parameters
    ----------
    path : str
        The path to the `Template`.

    """
    return Template(from_path=path)


def intercept(template=None):
    interceptor = Interceptor(template=template)
    interceptor.intercept()


def set_ip_forwarding(value):
    if platform.system() == "Linux":
        with open('/proc/sys/net/ipv4/ip_forward', 'w') as file:
            file.write(str(value))
            file.close()


def get_arpspoofer(targets, gateway, iface=None, gatewaymac=None,
                   ignore=None, arpmode='rep', mac=None, ip=None):
    # Creating a poison object
    poison = Poison(targets, gateway, gatewaymac, ignore,
                    arpmode, iface, mac, ip)
    # Creating an ARPpoisoner object
    poisoner = ARPpoisoner(poison)
    # return the poisoner
    return poisoner
