# Polymorph

Polymorph is a framework written in Python 3 that allows the modification of network packets in real time, providing maximum control to the user over the contents of the packet. This framework is intended to provide an effective solution for real-time modification of network packets that implement practically any existing protocol, including private protocols that do not have a public specification. In addition to this, one of its main objectives is to provide the user with the maximum possible control over the contents of the packet and with the ability to perform complex processing on this information.


# Installation

## Download and installation on Linux

Polymorph is specially designed to be installed and run on a Linux operating system, such as Kali Linux. Before installing the framework, the following requirements must be installed:

```
apt-get install build-essential python-dev libnetfilter-queue-dev tshark tcpdump python3-pip wireshark
```
After the installation of the dependencies, the framework itself can be installed with the Python pip package manager in the following way:
```
pip3 install polymorph
```

## Docker environment

From the project root:
```
docker-compose up -d
```
To access any of the machines of the environment:
```
docker exec -ti [polymorph | alice | bob] bash
```

# Using Polymorph

The Polymorph framework is composed of two main interfaces:

 - **Polymorph:** It consists of a command console interface. It is the main interface and it is recommended to use it for complex tasks such as modifying complex protocols in the air, making modifications of types in fields of the template or modifying protocols without public specification.
 - **Phcli:** It is the command line interface of the Polymorph framework. It is recommended to use for tasks such as modification of simple protocols or execution of previously generated templates.

## Using the Polymorph main interface
For examples and documentation please refer to:

-   [English whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_english.pdf)
-   [Spanish whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_spanish.pdf)
-   [Building a Proxy Fuzzer for the MQTT protocol with Polymorph](http://www.shramos.com/2018/04/building-proxy-fuzzer-for-mqtt-protocol.html)

## Using the Phcli

### Dissecting almost any network protocol
Let's start by seeing how Polymorph dissects the fields of different network protocols, it will be useful to refer to them if we want to modify any of this fields in real time. **You can try any protocol that comes to your mind.**

 - HTTP protocol, show only the HTTP layer and the fields belonging to it.
```
# phcli --protocol http --show-fields
```
- Show the full HTTP packet and the fields belonging to it.
```
# phcli --protocol http --show-packet
```
You can also apply filters on network packets, for example, you can indicate that only those containing a certain string or number are displayed.
```
# phcli -p dns --show-fields --in-pkt "phrack"
```
```
# phcli -p icmp --show-packet --in-pkt "84" --type "int"
```
- You can also concatenate filters.
```
# phcli -p http --show-packet --in-pkt "phrack;GET;issues"
```
```
# phcli -p icmp --show-packet --in-pkt "012345;84" --type "str;int"
```
- You can filter by the name of the fields that the protocol contains, but bear in mind that this name is the one that Polymorph provides when it dissects the network packet.
```
# phcli -p icmp --show-packet --field "chksum"
```
- You can also concatenate fields.
```
# phcli -p mqtt --show-packet --field "topic;msg"
```

### Modifying network packets in real time
Now that we know the Polymorph representation of the network packet that we want to modify, we will see how to modify it in real time.

Let's start with some examples. **All the filters explained during the previous section can also be applied here**. 
- This will just modify a packet that contains the strings `/issues/40/1.html` and `GET` by inserting in the `request_uri` field the value `/issues/61/1.html`. So when the user visit http://phrack.org/issues/40/1.html the browser will visit http://phrack.org/issues/61/1.html
```
# phcli -p http --field "request_uri" --value "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET"
```
- The previous command will work if we are in the middle of the communication between a machine and the gateway. Probably the user wants to establish himself in the middle, for this he can use arp spoofing.
```
# phcli --spoof arp --target 192.168.1.20 --gateway 192.168.1.1 -p http -f "request_uri" -v "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET"
```
- Or maybe the user wants to try it on localhost, for that he only has to modify the iptables rule that Polymorph establishes by default.
```
# phcli -p http -f "request_uri" -v "/issues/61/1.html" --in-pkt "/issues/40/1.html;GET" -ipt "iptables -A OUTPUT -j NFQUEUE --queue-num 1"
```
It may be the case that the user wants to modify a set of bytes of a network packet that have not been interpreted as a field by Polymorph. For this you can directly access the packet bytes using a slice. (*Remember to add the *iptables* rule if you try it in localhost*)
```
# phcli -p icmp --bytes "50:55" --value "hello" --in-pkt "012345"
```
```
# phcli -p icmp -b "\-6:\-1" --value "hello" --in-pkt "012345"
```
```
# phcli -p tcp -b "\-54:\-20" -v '"><script>alert("hacked")</script>' --in-pkt "</html>"
```

### Adding complex processing in real time

In certain situations it is possible that the PHCLI options are not enough to perform a certain action. For this, the framework implements the concept of conditional functions, which are functions written in Python that will be executed on the network packet that is intercepted in real time.
- The Conditional functions have the following format:
```
def precondition(packet):
    # Processing on the packet intercepted in real time
    return packet
```
- As a simple example, we are going to screen the raw bytes of the packets that we intercept. (*Remember to add the *iptables* rule if you try it in localhost*)
```
def execution(packet):
    print(packet.get_payload())
    return None
```
```
# phcli -p icmp --executions execution.py -v "None"
```
For more information about the power of the conditional functions, refer to:
-   [English whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_english.pdf)
-   [Spanish whitepaper](https://github.com/shramos/polymorph/blob/master/doc/whitepaper/whitepaper_spanish.pdf)

# Release Notes
[release-notes-1.0.0](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.0.md)\
[release-notes-1.0.3](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.3.md)

# Disclaimer
This program is published with the aim of being used for educational purposes and to help improve the security of the systems. I am not responsible for the misuse of this project.

# Contact

[shramos@protonmail.com](mailto:shramos@protonmail.com)
