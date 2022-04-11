# Polymorph

Polymorph is a tool that facilitates the modification of network traffic on the fly by allowing the execution of Python code on network packets that are intercepted in real time.

This framework can be used to modify in real time network packets that implement any publicly specified network protocol. Additionally, it can be used to modify privately specified network protocols by creating custom abstractions and fields.

# Installation

Polymorph is specially designed to be installed and run on a Linux operating system. Before installing the framework, the following requirements must be installed:
```
sudo apt install build-essential python3-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark git
```
After the installation of the dependencies, the framework itself can be installed with the Python pip package manager in the following way (to avoid errors, install Polymorph with the root user):
```
pip3 install git+https://github.com/kti/python-netfilterqueue
pip3 install polymorph
```

# Using Polymorph

Below you can find some resources and practical examples with which you can learn how Polymorph works. I recommend that you read the articles in the following order:  

0. [Setting up the enviroment](https://github.com/shramos/polymorph/wiki/Setting-up-the-enviroment)
1. [Case Study. Part 1: How does Polymorph work?](https://github.com/shramos/polymorph/wiki/Case-Study.-Part-1:-How-does-Polymorph-work%3F) (Modifying ICMP on the fly)
2. [Case Study. Part 2: Global variables](https://github.com/shramos/polymorph/wiki/Case-Study.-Part-2:-Global-variables) (Modifying ICMP on the fly)
3. [Case Study. Part 3: Structs](https://github.com/shramos/polymorph/wiki/Case-Study.-Part-3:-Structs) (Modifying MQTT on the fly)
4. [Case study. Part 4: Creating custom layers and fields](https://github.com/shramos/polymorph/wiki/Case-study.-Part-4:-Creating-custom-layers-and-fields) (Modifying MQTT on the fly)

# Important Release Notes 
[release-notes-2.0.4](https://github.com/shramos/polymorph/releases/tag/v2.0.4)  
[release-notes-2.0.0](https://github.com/shramos/polymorph/blob/master/docs/release-notes/release-notes-2.0.0.md)  
[release-notes-1.0.3](https://github.com/shramos/polymorph/blob/master/docs/release-notes/release-notes-1.0.3.md)  
[release-notes-1.0.0](https://github.com/shramos/polymorph/blob/master/docs/release-notes/release-notes-1.0.0.md)

# Disclaimer
This program is published with the aim of being used for educational purposes and to help improve the security of the systems. I am not responsible for the misuse of this project.

# Contact

[shramos@protonmail.com](mailto:shramos@protonmail.com)
