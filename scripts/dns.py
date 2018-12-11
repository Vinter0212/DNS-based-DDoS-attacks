import socket, glob, json, struct

port = 53
ip = '127.0.0.1'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', port))

def load_zones():

	jsonzone = {}
	zonefiles = glob.glob('zones/*.zone')

	for zone in zonefiles:
		with open(zone) as zonedata:
			data = json.load(zonedata)
			zonename = data["$origin"]
			jsonzone[zonename] = data
	return jsonzone

zonedata = load_zones()

def getflags(flags):

	byte1 = bytes(flags[:1])
	byte2 = bytes(flags[1:2])

	rflags = ''

	QR = '1'

	OPCODE = ''
	for bit in range(1,5):
		OPCODE += str(ord(byte1)&(1<<bit))

	AA = '1'

	TC = '0'

	RD = '0'

	# Byte 2

	RA = '0'

	Z = '000'

	RCODE = '0000'

	return struct.pack(">i", int(QR+OPCODE+AA+TC+RD, 2))+struct.pack(">i", int(RA+Z+RCODE, 2))

def getquestiondomain(data):

	state = 0
	expectedlength = 0
	domainstring = ''
	domainparts = []
	x = 0
	y = 0
	for byte in data:
		m_byte = int(byte.encode('hex'),16)
		if state == 1:
			if m_byte != 0:
				domainstring += chr(m_byte)
			x += 1 
			if x == expectedlength:
				domainparts.append(domainstring) 
				domainstring = ''
				state = 0
				x = 0
			if m_byte == 0:
				domainparts.append(domainstring)
				break
		else:
			state = 1
			expectedlength = m_byte
		y += 1

	questiontype = data[y:y+2]	
	#print domainparts
	return (domainparts, questiontype)

def getzone(domain):
	global zonedata

	zone_name = '.'.join(domain)
	# Check for existence of zone_name in zonedata
	#print zone_name	
	return zonedata[zone_name]

def getrecs(data):
	domain, questiontype = getquestiondomain(data)
	qt = ''
	if questiontype == b'\x00\x01':
		qt = 'a'
	zone = getzone(domain)
	return (zone[qt], qt, domain)

def buildquestion(domainname, rectype):
	qbytes = b''

	for part in domainname:
		length = len(part)
		qbytes += bytes([length])

		for char in part:
			qbytes += struct.pack(">i", ord(char))

	if rectype == 'a':
		qbytes += struct.pack(">i", 1)

	qbytes += struct.pack(">i", 1)

	return qbytes

def rectobytes(domainname, rectype, recttl, recval):

	rbytes = b'\xc0\x0c'

	if rectype == 'a':
		rbytes = rbytes + bytes([0]) + bytes([1])

	rbytes = rbytes + bytes([0]) + bytes([1])

	rbytes += struct.pack(">i", int(recttl))

	if rectype == 'a':
		rbytes = rbytes + bytes([0]) + bytes([4])

		for part in recval.split('.'):
			rbytes += bytes([int(part)])
	return rbytes

def buildresponse(data):

	# Transaction ID
	TransactionID = data[:2]

	# Get the flags
	Flags = getflags(data[2:4])

	# Question Count
	QDCOUNT = b'\x00\x01'

	# Answer Count
	ANCOUNT = struct.pack(">i", len(getrecs(data[12:])[0]))

	# Nameserver Count
	NSCOUNT = struct.pack(">i", 0)

	# Additonal Count
	ARCOUNT = struct.pack(">i", 0)

	dnsheader = TransactionID+Flags+QDCOUNT+ANCOUNT+NSCOUNT+ARCOUNT

	# Create DNS body
	dnsbody = b''

	# Get answer for query
	records, rectype, domainname = getrecs(data[12:])

	dnsquestion = buildquestion(domainname, rectype)

	for record in records:
		dnsbody += rectobytes(domainname, rectype, record["ttl"], record["value"])

	return dnsheader + dnsquestion + dnsbody


while True:
	data, addr = sock.recvfrom(512)
	r = buildresponse(data)
	print addr
	sock.sendto(r, addr)
