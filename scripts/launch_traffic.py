import sys
import getopt
import time
from os import popen
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from random import randrange


interface = popen('ifconfig | awk \'/eth0/ {print $1}\'').read()
while True:
	print ("sending packets")
	packets = Ether()/IP(dst="10.0.0.4", src="10.0.0.1")/UDP(dport=53, sport=80)/DNS(rd=1,qd=DNSQR(qname="howcode.org", qtype="A"))
    #print(packets)
    sendp(packets,iface=interface.rstrip(),inter=0.5)



