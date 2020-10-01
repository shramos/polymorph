# Polymorph

Polymorph is a tool that facilitates the modification of network traffic on the fly by allowing the execution of Python code on network packets that are intercepted in real time.

This framework can be used to modify on the fly network packets that implement any publicly specified network protocol. Additionally, it can be used to modify privately specified network protocols by creating custom abstractions and fields.

# Installation

Polymorph is specially designed to be installed and run on a Linux operating system. Before installing the framework, the following requirements must be installed:
```
apt-get install build-essential python-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark
```
After the installation of the dependencies, the framework itself can be installed with the Python pip package manager in the following way:
```
pip3 install git+https://github.com/kti/python-netfilterqueue
pip3 install polymorph
```
_\* More info: [Issue 8](https://github.com/shramos/polymorph/issues/8)_

# Using Polymorph
For more information on how to use Polymorph, please consult the wiki.

# Release Notes
[release-notes-1.0.3](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.3.md)  
[release-notes-1.0.0](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.0.md)

# Disclaimer
This program is published with the aim of being used for educational purposes and to help improve the security of the systems. I am not responsible for the misuse of this project.

# Contact

[shramos@protonmail.com](mailto:shramos@protonmail.com)