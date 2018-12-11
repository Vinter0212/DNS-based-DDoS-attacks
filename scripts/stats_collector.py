from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
import csv
# include as part of the betta branch
from pox.openflow.of_json import *

log = core.getLogger()

# handler for timer function that sends the requests to all the
# switches connected to the controller.
def _timer_func ():
  for connection in core.openflow._connections.values():
    connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
   # connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
  log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("FlowStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)

 
  web_bytes = 0
  web_flows = 0
  web_packet = 0
  for f in event.stats:
    if f.match.tp_dst == 53:
      web_bytes += f.byte_count
      web_packet += f.packet_count
      web_flows += 1
  log.info("Request Web traffic from %s: %s bytes (%s packets) over %s flows", 
    dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)
	
  web_bytes1 = 0
  web_flows1 = 0
  web_packet1 = 0
  for f in event.stats:
    if f.match.tp_src == 53:
      web_bytes1 += f.byte_count
      web_packet1 += f.packet_count
      web_flows1 += 1
  log.info("Response Web traffic from %s: %s bytes (%s packets) over %s flows", 
    dpidToStr(event.connection.dpid), web_bytes1, web_packet1, web_flows1)
	
  row = [web_packet, web_packet1, web_bytes1]
  with open('stats_norm.csv', 'a') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(row)
  csvFile.close()

# handler to display port statistics received in JSON format
"""def _handle_portstats_received (event):
  stats = flow_stats_to_list(event.stats)
  log.debug("PortStatsReceived from %s: %s", 
    dpidToStr(event.connection.dpid), stats)"""
    
# main functiont to launch the module
def launch ():
  from pox.lib.recoco import Timer

  # attach handsers to listners
  core.openflow.addListenerByName("FlowStatsReceived", 
    _handle_flowstats_received) 
 # core.openflow.addListenerByName("PortStatsReceived", 
 #   _handle_portstats_received) 

  # timer set to execute every five seconds
  Timer(10, _timer_func, recurring=True)