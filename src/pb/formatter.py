class Formatter:
    
    indentValue = 0
    short = False
    batch = False
    
    def __init__(self):
        self.longFormat()
    
    def shortFormat(self):
        self.short = True
    
    def longFormat(self):
        self.short = False
    
    def indent(self, indentModification):
        if indentModification is None:
            return " " * self.indentValue
        else:
            self.indentValue += indentModification
    
    def out(self, outStr = "", *args):
        print(("\t" * self.indentValue) + outStr % args)
    
    @staticmethod
    def requireArgs(soapResponse, requiredArgs, replaceMissingWith = "(none)"):
        result = {}
        for arg in requiredArgs:
            if arg in soapResponse:
                # fix non ascii
                if isinstance(soapResponse[arg], basestring):
                    result[arg] = soapResponse[arg].encode("UTF-8")
                else:
                    result[arg] = str(soapResponse[arg])
            else:
                result[arg] = replaceMissingWith
        return result
    
    # Generic method, for many operations that don't give any response (except through HTTP, which is handled by ProfitBricks.API)
    def operationQueued(self, response):
        self.out("Operation queued") # if you change this, remember to change it in test/test-pbapi.sh
    
    printClearDataCenter = operationQueued
    printUpdateDataCenter = operationQueued
    printRebootServer = operationQueued
    printDeleteDataCenter = operationQueued
    printUpdateServer = operationQueued
    printDeleteServer = operationQueued
    printDeleteStorage = operationQueued
    printConnectStorageToServer = operationQueued
    printDisconnectStorageFromServer = operationQueued
    printUpdateStorage = operationQueued
    printAddRomDriveToServer = operationQueued
    printRemoveRomDriveFromServer = operationQueued
    printSetImageOsType = operationQueued
    printDeleteImage = operationQueued
    printCreateNIC = operationQueued
    printEnableInternetAccess = operationQueued
    printDisableInternetAccess = operationQueued
    printUpdateNIC = operationQueued
    printDeleteNIC = operationQueued
    printAddPublicIPToNIC = operationQueued
    printRemovePublicIPFromNIC = operationQueued
    printReleasePublicIPBlock = operationQueued
    printDeleteLoadBalancer = operationQueued
    printDeregisterServersOnLoadBalancer = operationQueued
    printActivateLoadBalancingOnServers = operationQueued
    printDeactivateLoadBalancingOnServers = operationQueued
    printUpdateLoadBalancer = operationQueued
    printRemoveFirewallRule = operationQueued
    printActivateFirewall = operationQueued
    printDeactivateFirewall = operationQueued
    printDeleteFirewall = operationQueued
    
    def printCreateDataCenter(self, response):
        if self.batch:
            self.out(response["dataCenterId"])
            return
        self.out("Data center ID: %s", response["dataCenterId"])
        self.out("Data center region: %s", response["region"])
    
    def printCreateServer(self, response):
        if self.batch:
            self.out(response["serverId"])
            return
        self.out("Virtual server ID: %s", response["serverId"])
    
    def printCreateStorage(self, response):
        if self.batch:
            self.out(response["storageId"])
            return
        self.out("Virtual storage ID: %s", response["storageId"])
    
    def printDataCenterState(self, response):
        if self.batch:
            self.out(response)
            return
        self.out("Provisioning state: %s", response)
    
    def printAllDataCenters(self, dataCenters):
        if self.batch:
            for dataCenter in dataCenters:
                self.out(dataCenter["dataCenterId"])
            return
        if not self.short:
            self.out()
        self.out("%s %s %s %s", "Nr".ljust(3),  "Name".ljust(35), "Data Center ID".ljust(36), "Ver".ljust(4))
        self.out("%s %s %s %s", "-" * 3, "-" * 35, "-" * 36, "-" * 4)
        i = 1
        for dataCenter in dataCenters:
            dc = self.requireArgs(dataCenter, ["dataCenterName", "dataCenterId", "dataCenterVersion"]);
            self.out("%s %s %s %s", str(i).rjust(3), dc["dataCenterName"].ljust(35), dc["dataCenterId"].ljust(36), dc["dataCenterVersion"].ljust(4))
            i += 1
    
    def printNIC(self, apiNIC):
        nic = self.requireArgs(apiNIC, ["nicName", "nicId", "lanId", "macAddress", "serverId"])
        if self.short:
            self.out("NIC '%s' (%s MAC %s on server %s) => %s", nic["nicName"], "inet" if apiNIC["internetAccess"] else "priv", nic["macAddress"], nic["serverId"], " ; ".join(apiNIC["ips"]) if "ips" in apiNIC else "(no IPs)")
        else:
            self.out()
            self.out("Name: '%s'", nic["nicName"])
            self.out("NIC ID: %s", nic["nicId"])
            self.out("LAN ID: %s", nic["lanId"])
            self.out("Server ID: %s", nic["serverId"])
            self.out("Internet access: %s", "yes" if apiNIC["internetAccess"] else "no")
            self.out("IP Addresses: %s", " ; ".join(apiNIC["ips"]) if "ips" in apiNIC else "(none)")
            self.out("MAC Address: %s", nic["macAddress"])
            if "firewall" in apiNIC:
                self.out()
                self.indent(1)
                self.printFirewall(apiNIC["firewall"])
                self.indent(-1)
    
    def printServer(self, server):
        srv = self.requireArgs(server, ["serverName", "serverId", "creationTime", "lastModificationTime", "provisioningState", "virtualMachineState", "ram", "cores", "osType", "availabilityZone"])
        if self.short:
            self.out("'%s' => %s is %s and %s", srv["serverName"], srv["serverId"], srv["provisioningState"], srv["virtualMachineState"])
            self.indent(1)
            self.out("%s Cores ; %s MiB RAM ; OS: %s ; Internet access [%s]", srv["cores"], srv["ram"], srv["osType"], "yes" if server["internetAccess"] else "no")
            if "nics" in server:
                for nic in server.nics:
                    self.printNIC(nic);
            self.indent(-1)
        else:
            self.out()
            self.out("Name: '%s'", srv["serverName"])
            self.out("Server ID: %s", srv["serverId"])
            self.out("Created: [%s] Modified: [%s]", srv["creationTime"], srv["lastModificationTime"])
            self.out("Provisioning state: %s", srv["provisioningState"])
            self.out("Virtual machine state: %s", srv["virtualMachineState"])
            self.out("Cores: %s", srv["cores"])
            self.out("RAM: %s MiB", srv["ram"])
            self.out("Availability zone: %s", srv["availabilityZone"])
            self.out("Internet access: %s", "yes" if server["internetAccess"] else "no")
            self.out("Operating system: %s", srv["osType"])
            self.out("IP Addresses: %s", (" ; ".join(server.ips)) if "ips" in server else "(none)")
            if "nics" in server:
                self.indent(1)
                for nic in server.nics:
                    self.printNIC(nic);
                self.indent(-1)
            if "connectedStorages" in server or "romDrives" in server:
                self.out()
            if "connectedStorages" in server:
                self.indent(1)
                for sto in server.connectedStorages:
                    self.printConnectedStorage(sto)
                self.indent(-1)
            if "romDrives" in server:
                self.indent(1)
                for rom in server.romDrives:
                    self.printAddedRomDrive(rom)
                self.indent(-1)

    
    def printStorage(self, storage):
        st = self.requireArgs(storage, ["storageName", "storageId", "provisioningState", "size", "osType"])
        if self.short:
            self.out("'%s' => %s is %s", st["storageName"], st["storageId"], st["provisioningState"])
            self.indent(1)
            self.out("Size: %s GiB", st["size"])
            self.out("Connected to VM ID: %s", (" ; ".join(storage.serverIds)) if "serverIds" in storage else "(none)")
            if "mountImage" in storage:
                self._printStorageImage(storage.mountImage)
            else:
                self.out("(none)")
            self.indent(-1)
        else:
            self.out()
            self.out("Name: '%s'", st["storageName"])
            self.out("Storage ID: %s", st["storageId"])
            self.out("Size: %s GiB", st["size"])
            self.out("Connected to Virtual Servers: %s", (" ; ".join(storage.serverIds)) if "serverIds" in storage else "(none)")
            self.out("Provisioning state: %s", st["provisioningState"])
            self.out("Operating system: %s", st["osType"])
            self.out("Mount image:")
            self.indent(1)
            if "mountImage" in storage:
                self._printStorageImage(storage.mountImage)
            else:
                self.out("No image")
            self.indent(-1)

    def printConnectedStorage(self, storage):
        st = self.requireArgs(storage, ["storageName", "storageId", "deviceNumber", "busType"])
        self.out("Connected to Storage '%s' => %s on dev %s/%s", st["storageName"], st["storageId"], st["deviceNumber"], st["busType"])
        if "bootDevice" in storage:
            self.out("Boot Device: %s", storage["bootDevice"])

    def printAddedRomDrive(self, rom):
        st = self.requireArgs(rom, ["imageName", "imageId"])
        self.out("Connected to Rom drive '%s' => %s", st["imageName"], st["imageId"])    
        if "bootDevice" in rom:
            self.out("Boot Device: %s", rom["bootDevice"])
    
    def printCreateLoadBalancer(self, id):
        if self.batch:
            self.out(id)
            return
        self.out("Load balancer ID: %s", id)
    
    def printLoadBalancer(self, loadBalancer):
        if self.short:
            self.out("Load balancer '%s' => %s is %s, balancing %s on LAN %s => %s", loadBalancer["loadBalancerName"], loadBalancer["loadBalancerId"], loadBalancer["provisioningState"], loadBalancer["loadBalancerAlgorithm"], loadBalancer["lanId"], loadBalancer["ip"])
        else:
            self.out("Load balancer ID: %s", loadBalancer["loadBalancerId"])
            self.out("Name: '%s'", loadBalancer["loadBalancerName"])
            self.out("Provisioning state: %s", loadBalancer["provisioningState"])
            self.out("Algorithm: %s", loadBalancer["loadBalancerAlgorithm"])
            self.out("IP address: %s", loadBalancer["ip"] if "ip" in loadBalancer else "(none)")
            self.out("LAN ID: %s", loadBalancer["lanId"])
            self.out("Creation time [%s] modification time [%s]", loadBalancer["creationTime"] if "creationTime" in loadBalancer else "(None)", loadBalancer["lastModificationTime"] if "lastModificationTime" in loadBalancer else "(None)")
        self.out("Balanced servers:")
        self.indent(1)
        if "balancedServers" in loadBalancer:
            for srv in loadBalancer["balancedServers"]:
                self._printBalancedServer(srv)
        else:
            self.out("(none)")
        self.indent(-1)
        if not self.short:
            self.out()
        self.out("Firewall:")
        self.indent(1)
        if "firewall" in loadBalancer:
            self.printFirewall(loadBalancer.firewall)
        else:
            self.out("(none)")
        self.indent(-1)
    
    def _printBalancedServer(self, srv):
        # it may be "active" instead of "activate", but the documentation specifies it is "activate"
        if self.short:
            self.out("%s on server '%s' (%s) NIC %s", "Active" if srv["activate"] else "Inactive", srv["serverName"], srv["serverId"], srv["balancedNicId"])
        else:
            self.out()
            self.out("Server ID: %s", srv["serverId"])
            self.out("Server name: '%s'", srv["serverName"])
            self.out("NIC ID: %s", srv["balancedNicId"])
            self.out("Active: %s", "yes" if srv["activate"] else "no")
    
    def printRegisterServersOnLoadBalancer(self, response):
        self.out("Load balancer ID: %s", response["loadBalancerId"])
        self.out("LAN ID: %s", response["lanId"])
        if "balancedServers" in response:
            for srv in response["balancedServers"]:
                self._printBalancedServer(srv)
        else:
            self.out("ERROR")
    
    def _printStorageImage(self, image): # this is used by printStorage()
        if self.short:
            self.out("Image '%s' (%s)", image["imageName"], image["imageId"])
        else:
            self.out()
            self.out("Name: '%s'", image["imageName"])
            self.out("Image ID: %s", image["imageId"])
    
    def printImage(self, image): # used by all except printStorage()
        if self.short:
            self.out("Image '%s' (%s) in %s", image["imageName"], image["imageId"], image["region"] if "region" in image else "UNKNOWN_REGION")
        else:
            self.out()
            self.out("Name: '%s'", image["imageName"])
            self.out("Image ID: %s", image["imageId"])
            self.out("Region: %s", image["region"])
            self.out("Type: %s", image["imageType"])
            self.out("Writable: %s", "yes" if image["writeable"] else "nno")
            self.out("CPU hot plugging: %s", "yes" if image["cpuHotpluggable"] else "no")
            self.out("Memory hot plugging: %s", "yes" if image["memoryHotpluggable"] else "no")
            self.out("Server IDs: %s", (" ; ".join(image["serverIds"])) if "serverIds" in image else "(none)")
            self.out("Operating system: %s", image["osType"])
    
    def printAllImages(self, imageList):
        for i in imageList:
            self.printImage(i)
    
    def printDataCenter(self, dataCenter):
        dc = self.requireArgs(dataCenter, ["dataCenterName", "provisioningState", "dataCenterVersion", "region"])
        if self.short:
            self.out("Data center '%s' from %s is %s", dc["dataCenterName"], dc["region"], dc["provisioningState"])
            self.out("Servers (%d):", len(dataCenter.servers) if "servers" in dataCenter else 0)
            self.indent(1);
            if "servers" in dataCenter:
                for server in dataCenter.servers:
                    self.printServer(server)
            else:
                self.out("(none)")
            self.indent(-1);
            self.out("Storages (%s):", len(dataCenter.storages) if "storages" in dataCenter else 0)
            self.indent(1);
            if "storages" in dataCenter:
                for storage in dataCenter.storages:
                    self.printStorage(storage)
            else:
                self.out("(none)")
            self.indent(-1);
            self.out("Load balancers (%d):", len(dataCenter.loadBalancers) if "loadBalancers" in dataCenter else 0)
            self.indent(1);
            if "loadBalancers" in dataCenter:
                for loadBalancer in dataCenter.loadBalancers:
                    self.printLoadBalancer(loadBalancer)
            else:
                self.out("(none)")
            self.indent(-1);
        else:
            self.out()
            self.out("Name: '%s'", dc["dataCenterName"])
            self.out("Provisioning state: %s", dc["provisioningState"])
            self.out("Region: %s", dc["region"])
            self.out("Version: %s", dc["dataCenterVersion"])
            self.out()
            self.out("Servers (%d):", len(dataCenter.servers) if "servers" in dataCenter else 0)
            self.indent(1)
            if "servers" in dataCenter:
                for server in dataCenter.servers:
                    self.printServer(server)
            else:
                self.out("(none)")
            self.indent(-1)
            self.out()
            self.out("Storages (%s):", len(dataCenter.storages) if "storages" in dataCenter else 0)
            self.indent(1);
            if "storages" in dataCenter:
                for storage in dataCenter.storages:
                    self.printStorage(storage)
            else:
                self.out("(none)")
            self.indent(-1);
            self.out()
            self.out("Load balancers (%d):", len(dataCenter.loadBalancers) if "loadBalancers" in dataCenter else 0)
            self.indent(1);
            if "loadBalancers" in dataCenter:
                for loadBalancer in dataCenter.loadBalancers:
                    self.printLoadBalancer(loadBalancer)
            else:
                self.out("(none)")
            self.indent(-1);
    
    def printPublicIPBlock(self, ipBlock):
        if not self.short:
            self.out("IP Block %s in %s: %s", ipBlock["blockId"], ipBlock["region"], " ; ".join(ipBlock["ips"]))
        else:
            self.out()
            self.out("Block ID: %s", ipBlock["blockId"])
            self.out("IP addresses: %s", " ; ".join(ipBlock["ips"]))
            self.out("Region: %s", ipBlock["region"])
    
    def printGetAllPublicIPBlocks(self, blockList):
        for ipBlock in blockList:
            ips = []
            for ipObj in ipBlock.publicIps:
                ips.append(ipObj.ip)
            self.printPublicIPBlock({"blockId": ipBlock.blockId, "region": ipBlock.region, "ips": ips})
    
    def printAddFirewallRule(self, response):
        self.out("Firewall ID: %s", response.firewallId)
        self.out("NIC ID: %s", response.nicId)
        self.out("Provisioning state: %s", response.provisioningState)
        self.out("The firewall is %s", "ENABLED" if response.active else "DISABLED")
        self.out()
        print(response.firewallRules)
        self.out()
        print(response)
        self.out()

    def printFirewall(self, fw):
        self.out("Firewall ID: %s", fw.firewallId)
        self.out("NIC ID: %s", fw.nicId)
        self.out("Provisioning state: %s", fw.provisioningState)
        self.out("The firewall is %s", "ENABLED" if fw.active else "DISABLED")
        if "firewallRules" in fw:
            self.indent(1);
            for rule in fw.firewallRules:
                self.out()
                self.out("Firewall Rule ID: %s", rule.firewallRuleId)
                if "protocol" in rule:
                    self.out("Protocol: %s", rule.protocol)
                if "sourceMac" in rule:
                    self.out("Source Mac: %s", rule.sourceMac)
                if "sourceIp" in rule:
                    self.out("Source IP: %s", rule.sourceIp)
                if "targetIp" in rule:
                    self.out("Target IP: %s", rule.targetIp)
                if "portRangeStart" in rule:
                    self.out("Port range from %s to %s", rule.portRangeStart, rule.portRangeEnd)
                if "icmpType" in rule:
                    self.out("ICMP Type: %s", rule.icmpType)
                    self.out("ICMP Code: %s", rule.icmpCode)
            self.indent(-1);
        else:
            self.out("The firewall has no rules specified")