import errorhandler
# also import getpass, but only if it is needed (see below)

class ArgsParser:
	
	def __init__(self):
		self.baseArgs = {"s": False, "batch": False, "debug": False} # s = short output formatting, batch = batch output
		self.opArgs = {}
	
	def readUserArgs(self, argv):
		i = 1
		# -u -p -auth -debug and -s are base arguments, everything else are operation arguments
		# operation argument names are converted to lower-case and have dashes removed (eg, "create-datacenter -nA-Me hello" => baseArgs["op"]="create-datacenter", opArgs["name"]="hello")
		while i < len(argv):
			arg = argv[i].strip(" \r\n\t")
			if arg[0:1] == "#":
				# rest of line is comment, stop parsing
				break
			if arg == "-" or arg == "":
				i += 1
				continue
			# no dash = operation
			if arg[0] != "-":
				if "op" in self.baseArgs:
					errorhandler.ArgsError("Ambiguous argument '" + arg[0] + "'")
				else:
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
			elif arg.lower() == "-batch":
				self.baseArgs["batch"] = True
			elif arg.lower() == "-wait":
				self.baseArgs["wait"] = True
			elif arg.lower() == "-nowait":
				self.baseArgs["wait"] = False
			elif arg.lower() == "-f":
				if i == len(argv) - 1:
					errorhandler.ArgsError("Missing output format")
				self.baseArgs["f"] = argv[i + 1]
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
					return ''
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
				"api": lambda api, opArgs: api.createDataCenter(opArgs["name"], opArgs["region"] if "region" in opArgs else "DEFAULT"),
				"out": lambda formatter, result: formatter.printCreateDataCenter(result)
			},
			"getDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.getDataCenter(opArgs["dcid"]),
				"out": lambda formatter, result: formatter.printDataCenter(result)
			},
			"getDataCenterState": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.getDataCenterState(opArgs["dcid"]),
				"out": lambda formatter, result: formatter.printDataCenterState(result)
			},
			"getAllDataCenters": {
				"args": [],
				"api": lambda api, opArgs: api.getAllDataCenters(),
				"out": lambda formatter, result: formatter.printAllDataCenters(result)
			},
			"updateDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.updateDataCenter(opArgs),
				"out": lambda formatter, result: formatter.printUpdateDataCenter(result)
			},
			"clearDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.clearDataCenter(opArgs["dcid"]),
				"out": lambda formatter, result: formatter.printClearDataCenter(result)
			},
			"deleteDataCenter": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.deleteDataCenter(opArgs["dcid"]),
				"out": lambda formatter, result: formatter.printDeleteDataCenter(result)
			},
			"createServer": {
				"args": ["cores", "ram"],
				"api": lambda api, opArgs: api.createServer(opArgs),
				"out": lambda formatter, result: formatter.printCreateServer(result)
			},
			"getServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.getServer(opArgs["srvid"]),
				"out": lambda formatter, result: formatter.printServer(result)
			},
			"rebootServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.rebootServer(opArgs["srvid"]),
				"out": lambda formatter, result: formatter.printRebootServer(result)
			},
			"updateServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.updateServer(opArgs),
				"out": lambda formatter, result: formatter.printUpdateServer(result)
			},
			"deleteServer": {
				"args": ["srvid"],
				"api": lambda api, opArgs: api.deleteServer(opArgs["srvid"]),
				"out": lambda formatter, result: formatter.printDeleteServer(result)
			},
			"createStorage": {
				"args": ["size", "dcid"],
				"api": lambda api, opArgs: api.createStorage(opArgs),
				"out": lambda formatter, result: formatter.printCreateStorage(result)
			},
			"getStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.getStorage(opArgs["stoid"]),
				"out": lambda formatter, result: formatter.printStorage(result)
			},
			"connectStorageToServer": {
				"args": ["stoid", "srvid"],
				"api": lambda api, opArgs: api.connectStorageToServer(opArgs),
				"out": lambda formatter, result: formatter.printConnectStorageToServer(result)
			},
			"disconnectStorageFromServer": {
				"args": ["stoid", "srvid"],
				"api": lambda api, opArgs: api.disconnectStorageFromServer(opArgs["stoid"], opArgs["srvid"]),
				"out": lambda formatter, result: formatter.printDisconnectStorageFromServer(result)
			},
			"updateStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.updateStorage(opArgs),
				"out": lambda formatter, result: formatter.printUpdateStorage(result)
			},
			"deleteStorage": {
				"args": ["stoid"],
				"api": lambda api, opArgs: api.deleteStorage(opArgs["stoid"]),
				"out": lambda formatter, result: formatter.printDeleteStorage(result)
			},
			"createLoadBalancer": {
				"args": ["dcid"],
				"api": lambda api, opArgs: api.createLoadBalancer(opArgs),
				"out": lambda formatter, result: formatter.printCreateLoadBalancer(result)
			},
			"getLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.getLoadBalancer(opArgs["bid"]),
				"out": lambda formatter, result: formatter.printLoadBalancer(result)
			},
			"updateLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.updateLoadBalancer(opArgs),
				"out": lambda formatter, result: formatter.printUpdateLoadBalancer(result)
			},
			"registerServersOnLoadBalancer": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.registerServersOnLoadBalancer(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, result: formatter.printRegisterServersOnLoadBalancer(result)
			},
			"deregisterServersOnLoadBalancer": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.deregisterServersOnLoadBalancer(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, result: formatter.printDeregisterServersOnLoadBalancer(result)
			},
			"activateLoadBalancingOnServers": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.activateLoadBalancingOnServers(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, result: formatter.printActivateLoadBalancingOnServers(result)
			},
			"deactivateLoadBalancingOnServers": {
				"args": ["srvid", "bid"],
				"api": lambda api, opArgs: api.deactivateLoadBalancingOnServers(opArgs["srvid"].split(","), opArgs["bid"]),
				"out": lambda formatter, result: formatter.printDeactivateLoadBalancingOnServers(result)
			},
			"deleteLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.deleteLoadBalancer(opArgs["bid"]),
				"out": lambda formatter, result: formatter.printDeleteLoadBalancer(result)
			},
			"addRomDriveToServer": {
				"args": ["imgid", "srvid"],
				"api": lambda api, opArgs: api.addRomDriveToServer(opArgs),
				"out": lambda formatter, result: formatter.printAddRomDriveToServer(result)
			},
			"removeRomDriveFromServer": {
				"args": ["imgid", "srvid"],
				"api": lambda api, opArgs: api.removeRomDriveFromServer(opArgs),
				"out": lambda formatter, result: formatter.printRemoveRomDriveFromServer(result)
			},
			"setImageOsType": {
				"args": ["imgid", "ostype"],
				"api": lambda api, opArgs: api.setImageOsType(opArgs["imgid"], opArgs["ostype"]),
				"out": lambda formatter, result: formatter.printSetImageOsType(result)
			},
			"getImage": {
				"args": ["imgid"],
				"api": lambda api, opArgs: api.getImage(opArgs["imgid"]),
				"out": lambda formatter, result: formatter.printImage(result)
			},
			"getAllImages": {
				"args": [],
				"api": lambda api, opArgs: api.getAllImages(),
				"out": lambda formatter, result: formatter.printAllImages(result)
			},
			"deleteImage": {
				"args": ["imgid"],
				"api": lambda api, opArgs: api.deleteImage(opArgs["imgid"]),
				"out": lambda formatter, result: formatter.printDeleteImage(result)
			},
			"createNIC": {
				"args": ["srvid", "lanid"],
				"api": lambda api, opArgs: api.createNIC(opArgs),
				"out": lambda formatter, result: formatter.printCreateNIC(result)
			},
			"getNIC": {
				"args": ["nicid"],
				"api": lambda api, opArgs: api.getNIC(opArgs["nicid"]),
				"out": lambda formatter, result: formatter.printNIC(result)
			},
			"enableInternetAccess": {
				"args": ["dcid", "lanid"],
				"api": lambda api, opArgs: api.setInternetAccess(opArgs["dcid"], opArgs["lanid"], True),
				"out": lambda formatter, result: formatter.printEnableInternetAccess(result)
			},
			"disableInternetAccess": {
				"args": ["dcid", "lanid"],
				"api": lambda api, opArgs: api.setInternetAccess(opArgs["dcid"], opArgs["lanid"], False),
				"out": lambda formatter, result: formatter.printDisableInternetAccess(result)
			},
			"updateNic": {
				"args": ["nicid", "lanid"],
				"api": lambda api, opArgs: api.updateNIC(opArgs),
				"out": lambda formatter, result: formatter.printUpdateNIC(result)
			},
			"deleteNic": {
				"args": ["nicid"],
				"api": lambda api, opArgs: api.deleteNIC(opArgs["nicid"]),
				"out": lambda formatter, result: formatter.printDeleteNIC(result)
			},
			"reservePublicIpBlock": {
				"args": ["size"],
				"api": lambda api, opArgs: api.reservePublicIPBlock(opArgs["size"], opArgs["region"] if "region" in opArgs else "DEFAULT"),
				"out": lambda formatter, result: formatter.printPublicIPBlock(result)
			},
			"addPublicIpToNic": {
				"args": ["ip", "nicid"],
				"api": lambda api, opArgs: api.addPublicIPToNIC(opArgs["ip"], opArgs["nicid"]),
				"out": lambda formatter, result: formatter.printAddPublicIPToNIC(result)
			},
			"getAllPublicIpBlocks": {
				"args": [],
				"api": lambda api, opArgs: api.getAllPublicIPBlocks(),
				"out": lambda formatter, result: formatter.printGetAllPublicIPBlocks(result)
			},
			"removePublicIpFromNic": {
				"args": ["ip", "nicid"],
				"api": lambda api, opArgs: api.removePublicIPFromNIC(opArgs["ip"], opArgs["nicid"]),
				"out": lambda formatter, result: formatter.printRemovePublicIPFromNIC(result)
			},
			"releasePublicIpBlock": {
				"args": ["blockid"],
				"api": lambda api, opArgs: api.releasePublicIPBlock(opArgs["blockid"]),
				"out": lambda formatter, result: formatter.printReleasePublicIPBlock(result)
			},
			"addFirewallRuleToNic": {
				"args": ["nicId"],
				"api": lambda api, opArgs: api.addFirewallRuleToNic(opArgs["nicid"], opArgs),
				"out": lambda formatter, result: formatter.printAddFirewallRule(result)
			},
			"addFirewallRuleToLoadBalancer": {
				"args": ["bid"],
				"api": lambda api, opArgs: api.addFirewallRuleToLoadBalancer(opArgs["bid"], opArgs),
				"out": lambda formatter, result: formatter.printAddFirewallRule(result)
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

