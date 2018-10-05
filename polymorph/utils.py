# File from polymorph project
# Copyright (C) 2018 Santiago Hernandez Ramos <shramos@protonmail.com>
# For more information about the project: https://github.com/shramos/polymorph

from scapy.sendrecv import sniff
from scapy.utils import wrpcap, rdpcap
from polymorph.tgenerator import TGenerator
from polymorph.tlist import TList
from polymorph.template import Template
from polymorph.spoofs.arpspoof import ARPpoisoner
from polymorph.spoofs.poison import Poison
from polymorph.interceptor import Interceptor
import platform
import polymorph
from os.path import dirname, join
import imp, os, importlib

POLYM_PATH = dirname(polymorph.__file__)


def import_file(filename, module=""):
    """
    old stuff just for debug purposes
    # m = importlib.import_module(
    #     "polymorph.conditions.%s.%s" % (settings.paths[cond], name))
    # importlib.reload(m)

    """
    module = None

    try:
        # Get module name and path from full path
        module_dir, module_file = os.path.split(filename)
        module_name, module_ext = os.path.splitext(module_file)

        # Get module "spec" from filename
        spec = importlib.util.spec_from_file_location(module_name,filename)

        module = spec.loader.load_module()

    except Exception as ec:
        # TODO validate py2 importing if needed @shramos
        print(ec)

    finally:
        return module

    with open(filename, "r") as f:
        return imp.load_module(module, f, filename, "")


def capture(userfilter="", pcapname=".tmp.pcap", func=None, count=0, time=None):
    """This function is a wrapper function above the sniff scapy function. The
    result is a list of templates. The specification on filtering options can
    be found at: https://goo.gl/kVAmHQ

    Parameters
    ----------
    userfilter : :obj:`str`
        Filters to capture packets.
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
    if func:
        plist = sniff(filter=userfilter, prn=func, count=count,
                      timeout=time)
    else:
        plist = sniff(filter=userfilter, count=count, timeout=time)
    # Save the list of packages to disk for later readin with pyshark
    if len(plist) > 0:
        wrpcap(join(POLYM_PATH, pcapname), plist)
        tgen = TGenerator(join(POLYM_PATH, pcapname), scapy_pkts=plist)
        # Returns a list of templates
        return TList(tgen, len(plist), namesgen(plist))
    return None


def readpcap(pcapfile):
    """This function is a wrapper function above the generate function from
    TGenerator class. The result is a TemplatesList object.

    Parameters
    ----------
    pcapfile : :obj:`str`
        Path to a pcap file.

    Returns
    -------
    :obj: `TList`
        List of templates.

    """
    plist = rdpcap(pcapfile)
    tgen = TGenerator(pcapfile, scapy_pkts=plist)
    return TList(tgen, len(plist), namesgen(plist))


def pkt_to_template(pkt):
    """Generate a template from a Scapy packet.

    Parameters
    ----------
    pkt : :obj:`ScapyPkt`
        Packet generated by scapy.

    Returns
    -------
    :obj:`Template`
       Template that represents the packet.

    """
    wrpcap('.tmp.pcap', pkt)
    tgen = TGenerator('.tmp.pcap', scapy_pkts=pkt)
    return next(tgen)


def readtemplate(path):
    """This function reads a template from disk and returns its
    representation.

    Parameters
    ----------
    path : str
        The path to the `Template`.

    """
    return Template(from_path=path)


def namesgen(scapy_cap):
    """Generates a list of names for the templates.

    Parameters
    ----------
    scapy_cap : :obj:`PacketList`
        A capture from Scapy.

    Returns
    -------
    str
        A list of the names of the templates.

    """
    names = []
    for pkt in scapy_cap:
        layers = [pkt.__class__.__name__]
        while pkt.payload:
            pkt = pkt.payload
            layers.append(pkt.__class__.__name__)
        # Generating the name
        name = 'Template:%s' % ("/".join(layers))
        names.append(name)
    return names


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
