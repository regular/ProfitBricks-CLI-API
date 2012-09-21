import sys
import suds
import logging
import sudspatch
from suds.transport.http import HttpAuthenticated
from suds.transport import Request
import pb.client

class API:

    debug = False
    requestId = None
    datacenters = []
    proxy = None
    
    def __init__(self, username, password, debug = False):
        self.proxy = pb.client.ClientProxy(username, password, debug)
    
    # Returns the userArgs hash, but replaces the keys with the values found in translation and only the ones found in translation
    # eg, _parseArgs({"a": 10, "b": 20, "c": 30}, {"a": "a", "b": "B"}) => {"a": 10, "B": 20}
    def _parseArgs(self, userArgs, translation):
        args = {}
        for i in translation:
            if i.lower() in userArgs:
                args[translation[i]] = userArgs[i.lower()]
        return args
    
    def getAllDataCenters(self):
        result = self.proxy.getAllDataCenters()
        API.datacenters = result
        return result
    
    def getDataCenter(self, id):
        return self.proxy.getDataCenter(id)
    
    def getServer(self, id):
        return self.proxy.getServer(id)
    
    def createDataCenter(self, name, region):
        return self.proxy.createDataCenter(name, region)
    
    def getDataCenterState(self, id):
        return self.proxy.getDataCenterState(id)
    
    def updateDataCenter(self, userArgs):
        args = self._parseArgs(userArgs, {"dcid": "dataCenterId", "name": "dataCenterName"})
        return self.proxy.updateDataCenter(args)
    
    def clearDataCenter(self, id):
        return self.proxy.clearDataCenter(id)
    
    def deleteDataCenter(self, id):
        return self.proxy.deleteDataCenter(id)
    
    def createServer(self, userArgs):
        args = self._parseArgs(userArgs, {"cores": "cores", "ram": "ram", "bootFromStorageId": "bootFromStorageId", "bootFromImageId": "bootFromImageId", 
                                          "lanid": "lanId", "dcid": "dataCenterId", "name": "serverName", "ostype" : "osType", "zone" : "availabilityZone"})
        if "internetaccess" in userArgs:
            args["internetAccess"] = (userArgs["internetaccess"][:1].lower() == "y")
        return self.proxy.createServer(args)
    
    def rebootServer(self, id):
        return self.proxy.rebootServer(id)
    
    def updateServer(self, userArgs):
        args = self._parseArgs(userArgs, {"srvid": "serverId", "name": "serverName", "cores": "cores", "ram": "ram", "bootFromImageId": "bootFromImageId", 
                                          "bootFromStorageId": "bootFromStorageId", "ostype" : "osType", "zone" : "availabilityZone"})
        return self.proxy.updateServer(args)
    
    def deleteServer(self, id):
        return self.proxy.deleteServer(id)
    
    def createStorage(self, userArgs):
        args = self._parseArgs(userArgs, {"dcid": "dataCenterId", "size": "size", "name": "storageName", "imgid": "mountImageId"})
        return self.proxy.createStorage(args)
    
    def getStorage(self, id):
        return self.proxy.getStorage(id)
    
    def connectStorageToServer(self, userArgs):
        args = self._parseArgs(userArgs, {"stoid": "storageId", "srvid": "serverId", "devnum": "deviceNumber", "bus" : "busType"})
        return self.proxy.connectStorageToServer(args)
    
    def disconnectStorageFromServer(self, stoId, srvId):
        return self.proxy.disconnectStorageFromServer(stoId, srvId)
    
    def updateStorage(self, userArgs):
        args = self._parseArgs(userArgs, {"stoid": "storageId", "name": "storageName", "size": "size"})
        return self.proxy.updateStorage(args)
    
    def deleteStorage(self, id):
        return self.proxy.deleteStorage(id)
    
    def createLoadBalancer(self, userArgs):
        args = self._parseArgs(userArgs, {"dcid": "dataCenterId", "name": "loadBalancerName", "ip": "ip", "lanid": "lanId", "algo" : "loadBalancerAlgorithm"})
        if "srvid" in userArgs:
            args["serverIds"] = userArgs["srvid"].split(",")
        result = self.proxy.createLoadBalancer(args)
        return result.loadBalancerId
    
    def getLoadBalancer(self, id):
        return self.proxy.getLoadBalancer(id)
    
    def updateLoadBalancer(self, userArgs):
        args = self._parseArgs(userArgs, {"bid": "loadBalancerId", "name": "loadBalancerName", "ip": "ip", "algo" : "loadBalancerAlgorithm"})
        return self.proxy.updateLoadBalancer(args)
    
    def registerServersOnLoadBalancer(self, srvids, bid):
        return self.proxy.registerServersOnLoadBalancer(srvids, bid)
    
    def deregisterServersOnLoadBalancer(self, srvids, bid):
        return self.proxy.deregisterServersOnLoadBalancer(srvids, bid)
    
    def activateLoadBalancingOnServers(self, srvids, bid):
        return self.proxy.activateLoadBalancingOnServers(bid, srvids)
    
    def deactivateLoadBalancingOnServers(self, srvids, bid):
        return self.proxy.deactivateLoadBalancingOnServers(bid, srvids)
    
    def deleteLoadBalancer(self, id):
        return self.proxy.deleteLoadBalancer(id)
    
    def addRomDriveToServer(self, userArgs):
        args = self._parseArgs(userArgs, {"imgid": "imageId", "srvid": "serverId", "devnum": "deviceNumber"})
        return self.proxy.addRomDriveToServer(args)
    
    def removeRomDriveFromServer(self, id, srvid):
        return self.proxy.removeRomDriveFromServer(id, srvid)
    
    def setImageOsType(self, imgid, ostype):
        return self.proxy.setImageOsType(imgid, ostype)
    
    def getImage(self, id):
        return self.proxy.getImage(id)
    
    def getAllImages(self):
        return self.proxy.getAllImages()
    
    def createNIC(self, userArgs):
        args = self._parseArgs(userArgs, {"srvid": "serverId", "lanid": "lanId", "name": "nicName", "ip": "ip"})
        return self.proxy.createNic(args)
    
    def getNIC(self, id):
        return self.proxy.getNic(id)
    
    def setInternetAccess(self, dcid, lanid, internetAccess):
        return self.proxy.setInternetAccess(dcid, lanid, internetAccess)
    
    def updateNIC(self, userArgs):
        args = self._parseArgs(userArgs, {"nicid": "nicId", "lanid": "lanId", "name": "nicName"})
        if "ip" in userArgs:
            args["ip"] = (userArgs["ip"] if userArgs["ip"].lower() != "reset" else "")
        return self.proxy.updateNic(args)
    
    def deleteNIC(self, id):
        return self.proxy.deleteNic(id)
    
    def reservePublicIPBlock(self, size, region):
        return self.proxy.reservePublicIpBlock(size, region)
    
    def addPublicIPToNIC(self, ip, nicId):
        return self.proxy.addPublicIpToNic(ip, nicId)
    
    def getAllPublicIPBlocks(self):
        return self.proxy.getAllPublicIpBlocks()
    
    def removePublicIPFromNIC(self, ip, nicId):
        return self.proxy.removePublicIpFromNic(ip, nicId)
    
    def releasePublicIPBlock(self, id):
        return self.proxy.releasePublicIpBlock(id)
    
    def _parseFirewallRule(self, userRule):
        rule = self._parseArgs(userRule, {"smac": "sourceMac", "sip": "sourceIp", "dip": "targetIp", "icmptype": "icmpType", "icmpcode": "icmpCode"})
        if "proto" in userRule:
            rule["protocol"] = userRule["proto"].upper()
        if "port" in userRule:
            ports = userRule["port"].split("-")
            rule["portRangeStart"] = ports[0]
            rule["portRangeEnd"] = ports[len(ports) - 1]
        return rule
    
    def addFirewallRuleToNic(self, id, userRule):
        rule = self._parseFirewallRule(userRule)
        return self.proxy.addFirewallRuleToNic(rule, id)

    def removeFirewallRule(self, id):
        return self.proxy.removeFirewallRule(id)

    # provisioning not supported this function at the moment
    def addFirewallRuleToLoadBalancer(self, id, userRule):
        rule = self._parseFirewallRule(userRule)
        return self.proxy.addFirewallRuleToLoadBalancer(rule, id)

    def getFirewall(self, id):
        return self.proxy.getFirewall(id)

    def activateFirewall(self, id):
        return self.proxy.activateFirewall(id)

    def deactivateFirewall(self, id):
        return self.proxy.deactivateFirewall(id)

    def deleteFirewall(self, id):
        return self.proxy.deleteFirewall(id)
