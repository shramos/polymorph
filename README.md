# POLYMORPH

Polymoprh is a framework written in the Python3 programming language that allows the modification of network packets in real time, providing maximum control to the user over the contents of the packet. This framework is intended to provide an effective solution for real-time modification of network packets that implement practically any existing protocol, including private protocols that do not have a public specification. In addition to this, one of its main objectives is to provide the user with the maximum possible control over the contents of the packet and with the ability to perform complex processing on this information.

# INSTALLATION

## Download and installation on Linux (Recommended)

Polymoprh is specially designed to be installed and run on a Linux operating system, such as Kali Linux. Before installing the framework, the following requirements must be installed: 

    apt-get install build-essential python-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark

After the installation of the dependencies, the framework itself can be installed with the Python pip package manager in the following way:

    pip3 install --process-dependency-links polymorph

## Download and installation on Windows

Polymorph can also be installed on Windows operating systems. The requirements necessary for the framework to work correctly are the following:

 - Installation of Python3 (add it to *PATH*). [Download](https://www.python.org/downloads/)  
 - Installation of Wireshark (add it to the *PATH*). [Download](https://www.wireshark.org/download.html) 
 - Installation of Visual C    ++ Build Tools. [Download](https://www.visualstudio.com/en/thank-you-downloading-visual-studio/?sku=BuildTools%5C&rel=15) 
 - WinPcap installation (If you have not installed it with Wireshark) [Download](https://www.winpcap.org/install/default.htm)

Once the dependencies are installed, the only thing that the user must do is open a console and execute the following command.

    pip install --process-dependency-links polymorph

After completing the installation, Polymorph will be accessible from the terminal from any system path. It is important to note that **in Windows, Polymorph must be executed in a console with administrative privileges.**

## Docker enviroment
The implementation of this environment consists of three steps:

 - Download and install Docker on the host machine, to do so go to the Docker homepage and follow the installation instructions for the desired operating system.
 - Once the user has downloaded and started docker, he can access the project in the path */polymorph* and execute `docker-compose up -d`
 - Docker will then take care of creating the containers following the specifications set in the Dockerfile and in the YAML of the compose, as soon as the configuration is finished the three machines will be up and ready to be used. Each time the docker service is restarted, it will be necessary to execute `docker-compose up -d`
 - To access any of the machines the user must execute: `docker exec -ti [polymorph | alice | bob] bash`

# EXAMPLES AND DOCUMENTATION
For examples and documentation about the framework, please refer to:

 - [English whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_english.pdf)
 - [Spanish whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_spanish.pdf)
 - [Building a Proxy Fuzzer for the MQTT protocol with Polymorph](http://www.shramos.com/2018/04/building-proxy-fuzzer-for-mqtt-protocol.html)

# CONTACT
shramos@protonmail.com
