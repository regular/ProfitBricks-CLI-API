import sys
import suds
import logging
import sudspatch
from suds.transport.http import HttpAuthenticated
from suds.transport import Request

class API:
	
	url = "https://api.profitbricks.com/1.1/wsdl"
	debug = False
	requestId = None
	datacenters = []
	
	def __init__(self, username, password, debug = False):
		self.debug = debug
		if debug:
			logging.getLogger("suds.server").setLevel(logging.DEBUG)
			logging.getLogger("suds.client").setLevel(logging.DEBUG)
			logging.getLogger("suds.transport").setLevel(logging.DEBUG)
		else:
			logging.getLogger('suds.client').setLevel(logging.CRITICAL) # hide soap faults

		try:
			self.client = suds.client.Client(url = self.url, username = username, password = password)
		except suds.transport.TransportError as (err):
			raise Exception("Error: Invalid username or password" if err.httpcode == 401 else "Error: Unknown error: %s" % str(err.message))
	
	# Calls the func() function using SOAP and the given arguments list (must always be an array)
	def __call(self, func, args):
		if (self.debug):
			print "# Calling %s %s" % (func, args)
		try:
			method = getattr(self.client.service, func)
			result = method(*args)
			if self.requestId is None:
				if "requestId" in result:
					self.requestId = result["requestId"]
				else:
					self.requestId = "(no info)"
			if func == "getAllDataCenters":
				API.datacenters = result
			return result
		except suds.WebFault as (err):
			raise Exception("Error: %s" % str(err.message))
		except suds.transport.TransportError as (err):
			raise Exception("Error: Invalid username or password" if err.httpcode == 401 else "Error: Unknown error: %s" % str(err.message))
	
	# Returns the userArgs hash, but replaces the keys with the values found in translation and only the ones found in translation
	# eg, __parseArgs({"a": 10, "b": 20, "c": 30}, {"a": "a", "b": "B"}) => {"a": 10, "B": 20}
	def __parseArgs(self, userArgs, translation):
		args = {}
		for i in translation:
			if i.lower() in userArgs:
				args[translation[i]] = userArgs[i.lower()]
		return args
	
	def getAllDataCenters(self):
		return self.__call("getAllDataCenters", [])
	
	def getDataCenter(self, id):
		return self.__call("getDataCenter", [id])
	
	def getServer(self, id):
		return self.__call("getServer", [id])
	
	def createDataCenter(self, name):
		return self.__call("createDataCenter", [name])
	
	def getDataCenterState(self, id):
		return self.__call("getDataCenterState", [id])
	
	def updateDataCenter(self, userArgs):
		args = self.__parseArgs(userArgs, {"dcid": "dataCenterId", "name": "dataCenterName"})
		return self.__call("updateDataCenter", [args])
	
	def clearDataCenter(self, id):
		return self.__call("clearDataCenter", [id])
	
	def deleteDataCenter(self, id):
		return self.__call("deleteDataCenter", [id])
	
	def createServer(self, userArgs):
		args = self.__parseArgs(userArgs, {"cores": "cores", "ram": "ram", "bootFromStorageId": "bootFromStorageId", "bootFromImageId": "bootFromImageId", "lanId": "lanId", "dcid": "dataCenterId", "name": "serverName"})
		if "ostype" in userArgs:
			args["osType"] = userArgs["ostype"].upper()
		if "internetaccess" in userArgs:
			args["internetAccess"] = (userArgs["internetaccess"][:1].lower() == "y")
		return self.__call("createServer", [args])
	
	def rebootServer(self, id):
		return self.__call("rebootServer", [id])
	
	def updateServer(self, userArgs):
		args = self.__parseArgs(userArgs, {"srvid": "serverId", "name": "serverName", "cores": "cores", "ram": "ram", "bootFromImageId": "bootFromImageId", "bootFromStorageId": "bootFromStorageId", "osType": "osType"})
		return self.__call("updateServer", [args])
	
	def deleteServer(self, id):
		return self.__call("deleteServer", [id])
	
	def createStorage(self, userArgs):
		args = self.__parseArgs(userArgs, {"dcid": "dataCenterId", "size": "size", "name": "storageName", "imgid": "mountImageId"})
		return self.__call("createStorage", [args])
	
	def getStorage(self, id):
		return self.__call("getStorage", [id])
	
	def connectStorageToServer(self, userArgs):
		args = self.__parseArgs(userArgs, {"stoid": "storageId", "srvid": "serverId", "bus": "busType", "devnum": "deviceNumber"})
		args["busType"] = args["busType"].upper()
		return self.__call("connectStorageToServer", [args])
	
	def disconnectStorageFromServer(self, stoId, srvId):
		return self.__call("disconnectStorageFromServer", [stoId, srvId])
	
	def updateStorage(self, userArgs):
		args = self.__parseArgs(userArgs, {"stoid": "storageId", "name": "storageName", "size": "size", "imgid": "mountImageId"})
		return self.__call("updateStorage", [args])
	
	def deleteStorage(self, id):
		return self.__call("deleteStorage", [id])
	
	def createLoadBalancer(self, userArgs):
		args = self.__parseArgs(userArgs, {"dcid": "dataCenterId", "name": "loadBalancerName", "ip": "ip", "lanid": "lanId"})
		if "algo" in userArgs:
			args["loadBalancerAlgorithm"] = userArgs["algo"].upper()
		if "srvid" in userArgs:
			args["serverIds"] = userArgs["srvid"].split(",")
		result = self.__call("createLoadBalancer", [args])
		return result.loadBalancerId
	
	def getLoadBalancer(self, id):
		return self.__call("getLoadBalancer", [id])
	
	def updateLoadBalancer(self, userArgs):
		args = self.__parseArgs(userArgs, {"bid": "loadBalancerId", "name": "loadBalancerName", "ip": "ip"})
		if "algo" in userArgs:
			args["loadBalancerAlgorithm"] = userArgs["algo"].upper()
		return self.__call("updateLoadBalancer", [args])
	
	def registerServersOnLoadBalancer(self, srvids, bid):
		return self.__call("registerServersOnLoadBalancer", [srvids, bid])
	
	def deregisterServersOnLoadBalancer(self, srvids, bid):
		return self.__call("deregisterServersOnLoadBalancer", [srvids, bid])
	
	def activateLoadBalancingOnServers(self, srvids, bid):
		return self.__call("activateLoadBalancingOnServers", [srvids, bid])
	
	def deactivateLoadBalancingOnServers(self, srvids, bid):
		return self.__call("deactivateLoadBalancingOnServers", [srvids, bid])
	
	def deleteLoadBalancer(self, id):
		return self.__call("deleteLoadBalancer", [id])
	
	def addRomDriveToServer(self, userArgs):
		args = self.__parseArgs(userArgs, {"imgid": "imageId", "srvid": "serverId", "devnum": "deviceNumber"})
		return self.__call("addRomDriveToServer", [args])
	
	def removeRomDriveFromServer(self, id, srvid):
		return self.__call("addRomDriveToServer", [id, srvid])
	
	def setImageOsType(self, imgid, ostype):
		return self.__call("setImageOsType", [imgid, ostype])
	
	def getImage(self, id):
		return self.__call("getImage", [id])
	
	def getAllImages(self):
		return self.__call("getAllImages", [])
	
	def deleteImage(self, id):
		return self.__call("deleteImage", [id])
	
	def createNIC(self, userArgs):
		args = self.__parseArgs(userArgs, {"srvid": "serverId", "lanid": "lanId", "name": "nicName", "ip": "ip"})
		return self.__call("createNic", [args])
	
	def getNIC(self, id):
		return self.__call("getNic", [id])
	
	def setInternetAccess(self, dcid, lanid, internetAccess):
		return self.__call("setInternetAccess", [dcid, lanid, internetAccess])
	
	def updateNIC(self, userArgs):
		args = self.__parseArgs(userArgs, {"nicid": "nicId", "lanid": "lanId", "name": "nicName"})
		if "ip" in userArgs:
			args["ip"] = (userArgs["ip"] if userArgs["ip"].lower() != "reset" else "")
		return self.__call("updateNic", [args])
	
	def deleteNIC(self, id):
		return self.__call("deleteNic", [id])
	
	def reservePublicIPBlock(self, size):
		return self.__call("reservePublicIpBlock", [size])
	
	def addPublicIPToNIC(self, ip, nicId):
		return self.__call("addPublicIpToNic", [ip, nicId])
	
	def getAllPublicIPBlocks(self):
		result = self.__call("getAllPublicIpBlocks", [])
		return result
	
	def removePublicIPFromNIC(self, ip, nicId):
		return self.__call("removePublicIpFromNic", [ip, nicId])
	
	def releasePublicIPBlock(self, id):
		return self.__call("releasePublicIpBlock", [id])
	
	def __parseFirewallRule(self, userRule):
		rule = self.__parseArgs(userRule, {"smac": "sourceMac", "sip": "sourceIp", "dip": "targetIp", "icmptype": "icmpType", "icmpcode": "icmpCode"})
		if "proto" in userRule:
			rule["protocol"] = userRule["proto"].upper()
		if "port" in userRule:
			ports = userRule["port"].split(":")
			rule["portRangeStart"] = ports[0]
			rule["portRangeEnd"] = ports[len(ports) - 1]
		return rule
	
	def addFirewallRuleToNic(self, id, userRule):
		rule = self.__parseFirewallRule(userRule)
		return self.__call("addFirewallRuleToNic", [id, [rule]])
	
	def addFirewallRuleToLoadBalancer(self, id, userRule):
		rule = self.__parseFirewallRule(userRule)
		return self.__call("addFirewallRuleToLoadBalancer", [id, [rule]])
	

