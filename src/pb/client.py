# Profitbricks API proxy client
# Documentation is available at https://www.profitbricks.com/de/en/iaas-developer-center/profitbricks-api/apidoc/API%20Documentation.html for any references.
# All user related errors, bad requests or mandatory params etc., are checked on the server side by the Profitbricks API by each request.
# See examples in example.py
#
# Notice: in the same project you might find pbcli.py (a command line tool). 
# It wraps this client proxy with different names in functions and parameters for convenient typing
# @author tri.vohoang

import sys
import suds
import logging
import sudspatch
from suds.transport.http import HttpAuthenticated
from suds.transport import Request
from suds.xsd.doctor import Import, ImportDoctor
from suds.cache import ObjectCache

class ClientProxy:
    
    url = "https://api.profitbricks.com/1.2/wsdl"
    #url = "https://pbbde.profitbricks.localdomain/ProfitbricksApiService-1.2/ProfitbricksApiService?wsdl"
    
    debug = False
    requestId = None
    datacenters = []
    
    def __init__(self, username, password, debug = False):

        # suds has schema cache by default, here you can set manually
        oc = ObjectCache()
        oc.setduration(days=1)
        oc.setlocation("./cache")

        self.debug = debug
        if debug:
            logging.getLogger("suds.server").setLevel(logging.DEBUG)
            logging.getLogger("suds.client").setLevel(logging.DEBUG)
            logging.getLogger("suds.transport").setLevel(logging.DEBUG)
        else:
            logging.getLogger('suds.client').setLevel(logging.CRITICAL) # hide soap faults
        
        try:
            self.client = suds.client.Client(url = self.url, username = username, password = password, cache=None)
        except suds.transport.TransportError as (err):
            raise Exception("Authentication error: Invalid username or password." if err.httpcode == 401 else "Unknown initialization error: %s" % str(err))
    
    # Calls the func() function using SOAP and the given arguments list (must always be an array)
    def _call(self, func, args):
        if (self.debug):
            print("# Calling %s %s" % (func, args))
        try:
            method = getattr(self.client.service, func)
            result = method(*args)
            if self.requestId is None:
                if "requestId" in result:
                    self.requestId = result["requestId"]
                else:
                    self.requestId = "(no info)"
            return result
        except suds.WebFault as (err):
            raise Exception(str(err))
        except suds.transport.TransportError as (err):
            raise Exception("Authentication error: Invalid username or password." if err.httpcode == 401 else "Transport error: %s" % str(err))

    ############################################################################
    # DATA CENTER OPERATIONS
    ############################################################################

    def createDataCenter(self, name, region=''):
        """
        Create dc in the given region.
        Return a dict, information about the created dc:
        - `dataCenterId`
        - `region`

        Optional Parameters:
        - `name`: a string, name of the dc
        - `region`: a string, with possible values EUROPE, NORTH_AMERICA, DEFAULT or left empty
        """
        region = region.upper()
        if region not in ['', 'EUROPE', 'NORTH_AMERICA', 'DEFAULT']:
            raise Exception("Region not supported")
        return self._call("createDataCenter", [name, region])
    
    def getDataCenter(self, dataCenterId):
        """
        Return a dict, information about an existing dc state and configuration
        - `dataCenterName`:
        - `provisioningState`: a string, INACTIVE, INPROCESS, AVAILABLE, DELETED
        - `servers`: a list of server. See also getServer()
        - `storages`: a list of storage. See also getStorage()
        - `dataCenterVersion`:
        - `region`:
        - `loadBalancers`: a list of load balancer. See also getLoadBalancer()

        Required Parameters:
        - `dataCenterId`:
        """
        return self._call("getDataCenter", [dataCenterId])

    def getDataCenterState(self, dataCenterId):
        """
        A lightweight function of getDataCenter() for pooling the current provisioning state of the dc
        Return a string, INACTIVE, INPROCESS, AVAILABLE, DELETED

        Required Parameters:
        - `dataCenterId`:
        """
        return self._call("getDataCenterState", [dataCenterId])

    def getAllDataCenters(self):
        """
        Return a list of all data centers. Each has:
        - `dataCenterId`:
        - `dataCenterName`:
        - `dataCenterVersion`:
        """
        return self._call("getAllDataCenters", [])

    def updateDataCenter(self, updateDcRequest):
        """
        Update dc. Given a dict with

        Required Parameters:
        - `dataCenterId`:
        Optional Parameters:
        - `dataCenterName`:
        """
        return self._call("updateDataCenter", [updateDcRequest])
    
    def clearDataCenter(self, dataCenterId):
        """
        Clear a dc

        Required Parameters:
        - `dataCenterId`:
        """
        return self._call("clearDataCenter", [dataCenterId])

    def deleteDataCenter(self, dataCenterId):
        """
        Delete a dc

        Required Parameters:
        - `dataCenterId`:
        """
        return self._call("deleteDataCenter", [dataCenterId])

    ############################################################################
    # SERVER OPERATIONS
    ############################################################################    
    
    def createServer(self, createServerRequest):
        """
        Create a server
        Return a dict, information about the created server
        - `serverId`:

        Required Parameters:
        - `cores`: a number. For example: 1
        - `ram`: a number, in MiB. For example: 256
        Optional Parameters:
        - `dataCenterId`:
        - `serverName`:
        - `bootFromImageId`:
        - `bootFromStorageId`:
        - `lanId`:
        - `internetAccess`:
        - `availabilityZone`: ZONE_1, ZONE_2, AUTO, left empty
        - `osType`: WINDOWS, OTHER, empty
        """
        if "availabilityZone" in createServerRequest:
            createServerRequest['availabilityZone'] = createServerRequest['availabilityZone'].upper()
        if "osType" in createServerRequest:
            createServerRequest['osType'] = createServerRequest['osType'].upper()
        return self._call("createServer", [createServerRequest])

    def getServer(self, serverId):
        """
        Return a dict, runtime information about the server:
        - `serverName`:
        - `creationTime`:
        - `lastModificationTime`:
        - `provisioningState`:
        - `virtualMachineState`:
        - `cores`:
        - `ram`:
        - `internetAccess`:
        - `ips`:
        - `nics`:
        - `connectedStorages`: a list of connected storages. Each has:
            - `storageName`:
            - `storageId`:
            - `size`:
            - `busType`:
            - `deviceNumber`:
        - `romDrives`: a list of connected rom drives. Each has:
            - `imageName`:
            - `imageId`:
        - `availabilityZone`:
        - `osType`:

        Required Parameters:
        - `serverId`:
        """
        return self._call("getServer", [serverId])
    
    def updateServer(self, updateServerRequest):
        """
        Update server

        Required Parameters:
        - `serverId`:
        Optional Parameters:
        - `serverName`:
        - `cores`:
        - `ram`:
        - `bootFromImageId`:
        - `bootFromStorageId`:
        - `availabilityZone`: ZONE_1, ZONE_2, AUTO
        - `osType`:    WINDOWS, OTHER
        """
        if "availabilityZone" in updateServerRequest:
            updateServerRequest['availabilityZone'] = updateServerRequest['availabilityZone'].upper()
        if "osType" in updateServerRequest:
            updateServerRequest['osType'] = updateServerRequest['osType'].upper()
        return self._call("updateServer", [updateServerRequest])
    
    def rebootServer(self, serverId):
        """
        Reboot server

        Required Parameters:
        - `serverId`:
        """
        return self._call("rebootServer", [serverId])

    def deleteServer(self, serverId):
        """
        Del server

        Required Parameters:
        - `serverId`:
        """
        return self._call("deleteServer", [serverId])

    ############################################################################
    # STORAGE OPERATIONS
    ############################################################################
    
    def createStorage(self, createStorageRequest):
        """
        Create virtual storage
        Return a dict, information about the new created storage
        - `storageId`:

        Required Parameters:
        - `size`: a number, size in GiB
        Optional Parameters:
        - `dataCenterId`:
        - `storageName`:
        - `mountImageId`:
        """
        return self._call("createStorage", [createStorageRequest])
    
    def getStorage(self, storageId):
        """
        Returns runtime information about storage
        - `storageName`:
        - `creationTime`:
        - `lastModificationTime`:
        - `provisioningState`: a string, INACTIVE, INPROCESS, AVAILABLE, DELETED
        - `size`: a number, size in GiB
        - `serverIds`: a list of string
        - `mountImage`: a string, identifier of the copied image
        - `osType`: a string. OTHER, WINDOWS, UNKNOWN

        Required Parameters:
        - `storageId`:
        """
        return self._call("getStorage", [storageId])
    
    def connectStorageToServer(self, connectStorageRequest):
        """
        Connect storage to server

        Required Parameters:
        - `storageId`:
        - `serverId`:
        Optional Parameters:
        - `busType`: a string. IDE, SCSI, VIRTIO (default) or left empty
        - `deviceNumber`: a number
        """
        if "busType" in connectStorageRequest:
            connectStorageRequest["busType"] = connectStorageRequest["busType"].upper()
        return self._call("connectStorageToServer", [connectStorageRequest])
    
    def disconnectStorageFromServer(self, storageId, serverId):
        """
        Disconnect storage from server

        Required Parameters:
        - `storageId`:
        - `serverId`:
        """
        return self._call("disconnectStorageFromServer", [storageId, serverId])
    
    def updateStorage(self, updateStorageRequest):
        """
        Update storage

        Required Parameters:
        - `storageId`:
        Optional Parameters:
        - `storageName`:
        - `size`:
        """
        return self._call("updateStorage", [updateStorageRequest])
    
    def deleteStorage(self, storageId):
        """
        Del a storage

        Required Parameters:
        - `storageId`:
        """
        return self._call("deleteStorage", [storageId])

    ############################################################################
    # LOAD BALANCER OPERATIONS
    ############################################################################
    
    def createLoadBalancer(self, createLbRequest):
        """
        Create a lb
        Return a dict, information about the created lb
        - `loadBalancerId`:    

        Required Parameters:
        - `dataCenterId`:
        Optional Parameters:
        - `loadBalancerName`:
        - `loadBalancerAlgorithm`:
        - `ip`:
        - `lanId`:
        - `serverIds`:
        """
        if "loadBalancerAlgorithm" in createLbRequest:
            createLbRequest["loadBalancerAlgorithm"] = createLbRequest["loadBalancerAlgorithm"].upper()
        result = self._call("createLoadBalancer", [createLbRequest])
        return result
    
    def getLoadBalancer(self, loadBalancerId):
        """
        Return a dict, runtime information about given lb.
        - `creationTime`:
        - `lastModificationTime`:
        - `provisioningState`:
        - `loadBalancerName`:
        - `loadBalancerAlgorithm`:
        - `ip`:
        - `lanId`:
        - `balancedServers`:
            - `serverId`:
            - `serverName`:
            - `balancedNicId`:
            - `activate`:

        Required Parameters:
        - `loadBalancerId`:
        """
        return self._call("getLoadBalancer", [loadBalancerId])
    
    def updateLoadBalancer(self, updateLbRequest):
        """
        Update a given lb

        Required Parameters:
        - `loadBalancerId`:
        Optional Parameters:
        - `loadBalancerName`:
        - `loadBalancerAlgorithm`:
        - `ip`:
        """
        if "loadBalancerAlgorithm" in updateLbRequest:
            updateLbRequest["loadBalancerAlgorithm"] = updateLbRequest["loadBalancerAlgorithm"].upper()
        return self._call("updateLoadBalancer", [updateLbRequest])
    
    def registerServersOnLoadBalancer(self, serverIds, loadBalancerId):
        """
        Register server on lb. Servers will be connected to the lb on the same Lan
        If server is not on the same Lan with the lb, a new Nic is created on server and connect to the Lan of lb

        Required Parameters:
        - `serverIds`: list of one or more serverId
        - `loadBalancerId`:
        """
        return self._call("registerServersOnLoadBalancer", [serverIds, loadBalancerId])
    
    def deregisterServersOnLoadBalancer(self, serverIds, loadBalancerId):
        """
        Remove servers from lb but still remain on the same Lan

        Required Parameters:
        - `serverIds`: list of one or more serverId
        - `loadBalancerId`:
        """
        return self._call("deregisterServersOnLoadBalancer", [serverIds, loadBalancerId])    

    def activateLoadBalancingOnServers(self, loadBalancerId, serverIds):
        """
        Enables the load balancer to distribute traffic to the servers

        Required Parameters:
        - `loadBalancerId`:
        - `serverIds`: a list of one or more serverId
        """
        return self._call("activateLoadBalancingOnServers", [loadBalancerId, serverIds])
    
    def deactivateLoadBalancingOnServers(self, loadBalancerId, serverIds):
        """
        Disable the load balancer to distribute traffic to the servers

        Required Parameters:
        - `loadBalancerId`:
        - `serverIds`: a list of one or more serverId
        """
        return self._call("deactivateLoadBalancingOnServers", [loadBalancerId, serverIds])
    
    def deleteLoadBalancer(self, loadBalancerId):
        """
        Del lb

        Required Parameters:
        - `loadBalancerId`:
        """
        return self._call("deleteLoadBalancer", [loadBalancerId])

    ############################################################################
    # CDROM/DVD DRIVE OPERATIONS
    ############################################################################
    
    def addRomDriveToServer(self, romDriveRequest):
        """
        Mount iso image to a rom drive of the server

        Required Parameters:
        - `imageId`:
        - `serverId`:
        Optional Parameters:
        - `deviceNumber`:
        """
        return self._call("addRomDriveToServer", [romDriveRequest])
    
    def removeRomDriveFromServer(self, imageId, serverId):
        """
        Umount iso image from server

        Required Parameters:
        - `imageId`:
        - `serverId`:
        """
        return self._call("removeRomDriveFromServer", [imageId, serverId])
    
    ############################################################################
    # IMAGE OPERATIONS
    ############################################################################

    def setImageOsType(self, imageId, osType):
        """
        Set osType of image

        Required Parameters:
        - `imageId`:
        - `osType`: a string. WINDOWS, OTHER
        """
        if not osType:
            osType = osType.upper()
        return self._call("setImageOsType", [imageId, osType])

    def getImage(self, imageId):
        """
        Return a dict, information about an image
        - `imageId`:
        - `name`:
        - `imageSize`:
        - `imageType`:
        - `writeable`:
        - `region`:
        - `osType`:
        - `cpuHotpluggable:
        - `memoryHotpluggable`:
        - `serverIds`: a list of all serverId, which currently use the image in their rom drive

        Required Parameters:
        - `imageId`:
        """
        return self._call("getImage", [imageId])
    
    def getAllImages(self):
        """
        Get all Profitbricks image and customer uploaded images
        Return a list of Image. See also getImage()
        """
        return self._call("getAllImages", [])

    ############################################################################
    # NIC OPERATIONS
    ############################################################################

    def createNic(self, createNicRequest):
        """
        Create a nic on a server
        Return a dict, incl. information about the created nic
        - `nicId`:    

        Required Parameters:
        - `serverId`:
        - `lanId`:
        Optional Parameters:
        - `ip`:
        - `nicName`:
        """
        return self._call("createNic", [createNicRequest])
    
    def getNic(self, nicId):
        """
        Return a dict, runtime information about given nic
        - `nicName`:
        - `serverId`:
        - `lanId`:
        - `internetAccess`:
        - `ip`:
        - `macAddress`:

        Required Parameters:
        - `nicId`:
        """
        return self._call("getNic", [nicId])
    
    def setInternetAccess(self, dataCenterId, lanId, internetAccess):
        """
        Turn given lan of data center public or private

        Required Parameters:
        - `dataCenterId`:
        - `lanId`:
        - `internetAccess`: True/False for public/private
        Optional Parameters:
        - ``:
        """
        return self._call("setInternetAccess", [dataCenterId, lanId, internetAccess])
    
    def updateNic(self, updateNicRequest):
        """
        Update nic

        Required Parameters:
        - `nicId`:
        Optional Parameters:
        - `lanId`: a number, also to disconnect nic from any lan, set this to 0
        - `ip`:
        - `nicName`:
        """
        return self._call("updateNic", [updateNicRequest])
    
    def deleteNic(self, nicId):
        """
        Del nic

        Required Parameters:
        - `nicId`:
        """
        return self._call("deleteNic", [nicId])
    
    ############################################################################
    # PUBLIC IPs
    # (customer reserved ip address)
    ############################################################################

    def reservePublicIpBlock(self, blockSize, region):
        """
        Reserve an ip block
        Return a dict, information about the reserved ip block
        - `blockId`:
        - `ips`: a list of ip in string format
        - `region`:

        Required Parameters:
        - `blockSize`:
        Optional Parameters:
        - `region`: a string. EUROPE, NORTH_AMERICA, DEFAULT or left empty
        """
        if not region:
            region = region.upper()
        return self._call("reservePublicIpBlock", [blockSize, region])
    
    def addPublicIpToNic(self, ip, nicId):
        """
        Add additional public ip to a nic

        Required Parameters:
        - `ip`:
        - `nicId`:
        """
        return self._call("addPublicIpToNic", [ip, nicId])
    
    def getAllPublicIpBlocks(self):
        """
        Return a list of all reserved ip blocks. Each has
        - `blockId`:
        - `region`:
        - `publicIps`: a list of ip in the given block. Each has
            - `ip`: ip in string
            - `nicId`: a string, identifier of a nic if this ip currently assigned to it
        """
        result = self._call("getAllPublicIpBlocks", [])
        return result
    
    def removePublicIpFromNic(self, ip, nicId):
        """
        Remove a reserved ip from a given nic

        Required Parameters:
        - `ip`:
        - `nicId`:
        """
        return self._call("removePublicIpFromNic", [ip, nicId])
    
    def releasePublicIpBlock(self, blockId):
        """
        Relase a block ip. Ip must be freed from any nics first

        Required Parameters:
        - `blockId`:
        """
        return self._call("releasePublicIpBlock", [blockId])
    
    ############################################################################
    # FIREWALL OPERATIONS
    ############################################################################

    def addFirewallRuleToNic(self, firewallRuleRequest, nicId):
        """
        Add an accept rule to a given nic
        Return a dict, information about the new firewall created on the nic
        - `firewallId`:
        - `nicId`:
        - `provisioningState`:
        - `active`:
        - `firewallRules`: a list of added rules
            - `firewallRuleId`:
            - `protocol`:
            - `sourceMac`:
            - `sourceIp`:
            - `targetIp`:
            - `portRangeStart`: 
            - `portRangeEnd`: 
            - `icmpType`: 
            - `icmpCode`:

        Required Parameters:
        - `firewallRuleRequest`: a dict for rule request
            - `protocol`:
            - `sourceMac`:
            - `sourceIp`:
            - `targetIp`:
            - `portRangeStart`:
            - `portRangeEnd`:
            - `icmpType`: 
            - `icmpCode`:    
        - `nicId`:
        """
        return self._call("addFirewallRulesToNic", [[firewallRuleRequest], nicId])

    def getFirewall(self, firewallId):
        """
        Return a dict, runtime information about given firewall
        - `firewallId`:
        - `nicId`:
        - `provisioningState`:
        - `active`:
        - `firewallRules`: a list of added rules
            - `firewallRuleId`:
            - `protocol`:
            - `sourceMac`:
            - `sourceIp`:
            - `targetIp`:
            - `portRangeStart`: 
            - `portRangeEnd`: 
            - `icmpType`: 
            - `icmpCode`:

        Required Parameters:
        - `firewallId`:
        """
        return self._call("getFirewall", [firewallId])

    def removeFirewallRule(self, firewallRuleId):
        """
        Remove a firewall rule by id
        
        Required Parameters:
        - `firewallRuleId`:
        """
        return self._call("removeFirewallRules", [firewallRuleId])

    def activateFirewall(self, firewallId):
        """
        Activate a firewall

        Required Parameters:
        - `firewallId`:
        """
        return self._call("activateFirewalls", [firewallId])

    def deactivateFirewall(self, firewallId):
        """
        Deactivate a firewall

        Required Parameters:
        - `firewallId`:
        """
        return self._call("deactivateFirewalls", [firewallId])

    def deleteFirewall(self, firewallId):
        """
        Del a firewall
        
        Required Parameters:
        - `firewallId`:
        """
        return self._call("deleteFirewalls", [firewallId])
