import errorhandler

class ArgsParser:
	
	def __init__(self):
		self.baseArgs = {"s": False, "debug": False} # s = short output formatting
		self.opArgs = {}
	
	def readUserArgs(self, argv):
		i = 1
		# -u -p -auth -debug and -s are base arguments, everything else are operation arguments
		# operation argument names are converted to lower-case and have dashes removed (eg, "create-datacenter -nA-Me hello" => baseArgs["op"]="create-datacenter", opArgs["name"]="hello")
		while i < len(argv):
			arg = argv[i].strip(" \r\n\t")
			if arg == "-" or arg == "":
				i += 1
				continue
			# no dash = operation
			if arg[0] != "-":
				if not "op" in self.baseArgs:
					self.baseArgs["op"] = argv[i]
				i += 1
				continue
			# base args
			if arg.lower() == "-u":
				if i == len(argv) - 1:
					errorhandler.ArgsError("Missing username")
				self.baseArgs["u"] = argv[i + 1]
				i += 1
			elif arg.lower() == "-p":
				if (i == len(argv) - 1) or (argv[i + 1][0] == "-"):
					import getpass
					self.baseArgs["p"] = getpass.getpass()
				else:
					self.baseArgs["p"] = argv[i + 1]
				i += 1
			elif arg.lower() == "-auth":
				if i == len(argv) - 1:
					errorhandler.ArgsError("Missing authfile")
				self.baseArgs["auth"] = argv[i + 1]
				try:
					authFile = open(argv[i + 1], "r")
					self.baseArgs["u"] = authFile.readline().strip("\n")
					self.baseArgs["p"] = authFile.readline().strip("\n")
					authFile.close()
				except:
					errorhandler.ArgsError("Authfile does not exist or cannot be read")
				i += 1
			elif arg.lower() == "-debug":
				self.baseArgs["debug"] = True
			elif arg.lower() == "-s":
				self.baseArgs["s"] = True
			# if not base arg, then it is operation arg
			else:
				self.opArgs[arg[1:].lower().replace("-", "")] = (argv[i + 1] if i < len(argv) - 1 else "")
				i += 1
			i += 1
		
		if "op" not in self.baseArgs:
			errorhandler.ArgsError("Missing operation")
		
		self._loadAuthFile()
	
	def getRequestedOperation(self):
		userOperation = self.baseArgs["op"].replace("-", "").lower()
		for op in ArgsParser.operations:
			if '@' + userOperation == op.replace("-", "").lower():
				return op
			if userOperation != op.replace("-", "").lower():
				continue
			for requiredArg in ArgsParser.operations[op]["args"]:
				if not requiredArg in self.opArgs:
					errorhandler.ArgsError("operation '%s' requires these arguments: -%s" % (self.baseArgs["op"], " -".join(ArgsParser.operations[op]["args"])))
					return op
			return op
		return None
	
	def _loadAuthFile(self):
		if "u" not in self.baseArgs or "p" not in self.baseArgs:
			try:
				authFile = open("./default.auth", "r")
				self.baseArgs["u"] = authFile.readline().strip("\n")
				self.baseArgs["p"] = authFile.readline().strip("\n")
				authFile.close()
			except:
				pass
	
	def isAuthenticated(self):
		return "u" in self.baseArgs and "p" in self.baseArgs
	
	operations = {
			"createDataCenter": {
				"args": ["name"],
				"api": lambda api, opArgs: api.createDataCenter(opArgs["name"]),
				"out": lambda formatter, apiResult: formatter.printCreateDataCenter(apiResult)
			},
			"getDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.getDataCenter(opArgs["dcid"]),
				"out": lambda formatter, apiResult: formatter.printDataCenter(apiResult)
			},
			"getDataCenterState": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.getDataCenterState(opArgs["dcid"]),
				"out": lambda formatter, apiResult: formatter.printDataCenterState(apiResult)
			},
			"getAllDataCenters": {
				"args": [],
				"api": lambda api, opArgs: api.getAllDataCenters(),
				"out": lambda formatter, apiResult: formatter.printAllDataCenters(apiResult)
			},
			"updateDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.updateDataCenter(opArgs),
				"out": lambda formatter, apiResult: formatter.printUpdateDataCenter(apiResult)
			},
			"clearDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.clearDataCenter(opArgs["dcid"]),
				"out": lambda formatter, apiResult: formatter.printClearDataCenter(apiResult)
			},
			"deleteDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.deleteDataCenter(opArgs["dcid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteDataCenter(apiResult)
			},
			"createServer": {
				"args": ["cores", "ram"],
				"api": lambda api, opArgs: api.createServer(opArgs),
				"out": lambda formatter, apiResult: formatter.printCreateServer(apiResult)
			},
			"getServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.getServer(opArgs["srvid"]),
				"out": lambda formatter, apiResult: formatter.printServer(apiResult)
			},
			"rebootServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.rebootServer(opArgs["srvid"]),
				"out": lambda formatter, apiResult: formatter.printRebootServer(apiResult)
			},
			"updateServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.updateServer(opArgs),
				"out": lambda formatter, apiResult: formatter.printDataCenter(apiResult)
			},
			"deleteServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.deleteServer(opArgs["srvid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteServer(apiResult)
			},
			"createStorage": {
				"args": ["size", "dcid"],
				"api": lambda api, opArgs: api.createStorage(opArgs),
				"out": lambda formatter, apiResult: formatter.printCreateStorage(apiResult)
			},
			"getStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.getStorage(opArgs["stoid"]),
				"out": lambda formatter, apiResult: formatter.printStorage(apiResult)
			},
			"connectStorageToServer": {
				"args": ["stoid", "srvid", "bus"],
				"api": lambda api, opArgs: api.connectStorageToServer(opArgs),
				"out": lambda formatter, apiResult: formatter.printConnectStorageToServer(apiResult)
			},
			"disconnectStorageFromServer": {
				"args": ["stoid", "srvid"],
				"api": lambda api, opArgs: api.disconnectStorageFromServer(opArgs["stoid"], opArgs["srvid"]),
				"out": lambda formatter, apiResult: formatter.printDisconnectStorageFromServer(apiResult)
			},
			"updateStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.updateStorage(opArgs),
				"out": lambda formatter, apiResult: formatter.printUpdateStorage(apiResult)
			},
			"deleteStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.deleteStorage(opArgs["stoid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteStorage(apiResult)
			},
			"createLoadBalancer": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.createLoadBalancer(opArgs),
				"out": lambda formatter, apiResult: formatter.printCreateLoadBalancer(apiResult)
			},
			"getLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.getLoadBalancer(opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printLoadBalancer(apiResult)
			},
			"updateLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.updateLoadBalancer(opArgs),
				"out": lambda formatter, apiResult: formatter.printUpdateLoadBalancer(apiResult)
			},
			"registerServersOnLoadBalancer": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.registerServersOnLoadBalancer(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printRegisterServersOnLoadBalancer(apiResult)
			},
			"deregisterServersOnLoadBalancer": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.deregisterServersOnLoadBalancer(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printDeregisterServersOnLoadBalancer(apiResult)
			},
			"activateLoadBalancingOnServers": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.activateLoadBalancingOnServers(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printActivateLoadBalancingOnServers(apiResult)
			},
			"deactivateLoadBalancingOnServers": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.deactivateLoadBalancingOnServers(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printDeactivateLoadBalancingOnServers(apiResult)
			},
			"deleteLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.deleteLoadBalancer(opArgs["bid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteLoadBalancer(apiResult)
			},
			"addRomDriveToServer": {
				"args": ["imgid", "srvid"],
				"api": lambda api, opArgs: api.addRomDriveToServer(opArgs),
				"out": lambda formatter, apiResult: formatter.printAddRomDriveToServer(apiResult)
			},
			"removeRomDriveFromServer": {
				"args": ["imgid", "srvid"],
				"api": lambda api, opArgs: api.removeRomDriveFromServer(opArgs),
				"out": lambda formatter, apiResult: formatter.printRemoveRomDriveFromServer(apiResult)
			},
			"setImageOsType": {
				"args": ["imgid", "ostype"],
				"api": lambda api, opArgs: api.setImageOsType(opArgs["imgid"], opArgs["ostype"]),
				"out": lambda formatter, apiResult: formatter.printSetImageOsType(apiResult)
			},
			"getImage": {
				"args": ["imgid"],
				"api": lambda api, opArgs: api.getImage(opArgs["imgid"]),
				"out": lambda formatter, apiResult: formatter.printImage(apiResult)
			},
			"getAllImages": {
				"args": [],
				"api": lambda api, opArgs: api.getAllImages(),
				"out": lambda formatter, apiResult: formatter.printAllImages(apiResult)
			},
			"deleteImage": {
				"args": ["imgid"],
				"api": lambda api, opArgs: api.deleteImage(opArgs["imgid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteImage(apiResult)
			},
			"createNIC": {
				"args": ["srvid", "lanid"],
				"api": lambda api, opArgs: api.createNIC(opArgs),
				"out": lambda formatter, apiResult: formatter.printCreateNIC(apiResult)
			},
			"getNIC": {
				"args": ["nicid"],
				"api": lambda api, opArgs: api.getNIC(opArgs["nicid"]),
				"out": lambda formatter, apiResult: formatter.printNIC(apiResult)
			},
			"enableInternetAccess": {
				"args": ["dcid", "lanid"],
				"api": lambda api, opArgs: api.setInternetAccess(opArgs["dcid"], opArgs["lanid"], True),
				"out": lambda formatter, apiResult: formatter.printEnableInternetAccess(apiResult)
			},
			"disableInternetAccess": {
				"args": ["dcid", "lanid"],
				"api": lambda api, opArgs: api.setInternetAccess(opArgs["dcid"], opArgs["lanid"], False),
				"out": lambda formatter, apiResult: formatter.printDisableInternetAccess(apiResult)
			},
			"updateNic": {
				"args": ["nicid", "lanid"],
				"api": lambda api, opArgs: api.updateNIC(opArgs),
				"out": lambda formatter, apiResult: formatter.printUpdateNIC(apiResult)
			},
			"deleteNic": {
				"args": ["nicid"],
				"api": lambda api, opArgs: api.deleteNIC(opArgs["nicid"]),
				"out": lambda formatter, apiResult: formatter.printDeleteNIC(apiResult)
			},
			"reservePublicIpBlock": {
				"args": ["size"],
				"api": lambda api, opArgs: api.reservePublicIPBlock(opArgs["size"]),
				"out": lambda formatter, apiResult: formatter.printPublicIPBlock(apiResult)
			},
			"addPublicIpToNic": {
				"args": ["ip", "nicid"],
				"api": lambda api, opArgs: api.addPublicIPToNIC(opArgs["ip"], opArgs["nicid"]),
				"out": lambda formatter, apiResult: formatter.printAddPublicIPToNIC(apiResult)
			},
			"getAllPublicIpBlocks": {
				"args": [],
				"api": lambda api, opArgs: api.getAllPublicIPBlocks(),
				"out": lambda formatter, apiResult: formatter.printGetAllPublicIPBlocks(apiResult)
			},
			"removePublicIpFromNic": {
				"args": ["ip", "nicid"],
				"api": lambda api, opArgs: api.removePublicIPFromNIC(opArgs["ip"], opArgs["nicid"]),
				"out": lambda formatter, apiResult: formatter.printRemovePublicIPFromNIC(apiResult)
			},
			"releasePublicIpBlock": {
				"args": ["blockid"],
				"api": lambda api, opArgs: api.releasePublicIPBlock(opArgs["blockid"]),
				"out": lambda formatter, apiResult: formatter.printReleasePublicIPBlock(apiResult)
			},
			"addFirewallRuleToNic": {
				"args": ["nicId"],
				"api": lambda api, opArgs: api.addFirewallRuleToNic(opArgs["nicid"], opArgs),
				"out": lambda formatter, apiResult: formatter.printAddFirewallRule(apiResult)
			},
			"addFirewallRuleToLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.addFirewallRuleToLoadBalancer(opArgs["bid"], opArgs),
				"out": lambda formatter, apiResult: formatter.printAddFirewallRule(apiResult)
			},
			"@list": {
				"args": [],
				"api": lambda helper: helper.printOperations(ArgsParser.operations)
			},
			"@list-simple": {
				"args": [],
				"api": lambda helper: helper.printOperationsSimple(ArgsParser.operations)
			}
		}

