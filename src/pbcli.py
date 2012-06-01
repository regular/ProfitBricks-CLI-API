#!/usr/bin/python

import readline
import sys
import re
import time
import platform
import os
import shlex
import pb.api
import pb.argsparser
import pb.helper
import pb.formatter
import pb.errorhandler
import pb.spellcheck

class Shell:

	version = '1.1'

	cmds_internal = {}
	cmds_api = pb.argsparser.ArgsParser().operations
	tbold = '\033[1m'
	treset = '\033[0;0m'

	default_dc = None
	wait = True

	def __init__(self):
		this = self
		self.cmds_internal = {
			'help': lambda args: this.do_help(),
			'use': lambda args: this.do_use(args),
			'exit': lambda args: this.do_exit(),
			'q': lambda args: this.do_exit(),
			'quit': lambda args: this.do_exit(),
			'bye': lambda args: this.do_exit(),
			'wait': lambda args: this.do_wait(),
			'nowait': lambda args: this.do_nowait(),
			'about': lambda args: this.do_about()
		}
		pb.errorhandler.initializing += 1
		temp_out = pb.formatter.Formatter.out
		pb.formatter.Formatter.out = lambda *args: this.do_nothing()
		self.parse("getAllDataCenters")
		pb.formatter.Formatter.out = temp_out
		pb.errorhandler.initializing -= 1

	def out(self, text):
		pb.formatter.Formatter.out(pb.formatter.Formatter(), text)

	def prompt(self):
		return self.treset + self.tbold + ('ProfitBricks> ' if self.default_dc is None else self.default_dc + '> ') + self.treset

	def completer(self):
		this = self
		
		def inner_completer(text, state):
			text = text.replace('-', '').lower()
			matches = []
			for cmd in this.cmds_internal:
				if cmd.replace('-', '').lower().startswith(text):
					matches.append(cmd)
			for cmd in this.cmds_api:
				if cmd.replace('-', '').lower().startswith(text):
					matches.append(cmd)
			return pb.helper.Helper.camelCaseToDash(matches[state]) + ' ' if state < len(matches) else None
		
		return inner_completer

	def run_command(self, cmd, args):
		if cmd == 'deleteDataCenter' and self.default_dc is not None:
			self.out('Data center ' + self.default_dc + ' is in use. You may not perform any data center deletion operations. Type \'use\' to reset and try again\n')
			return
		args.insert(0, 'dummy') # equivalent of argv[0]
		argsParser = pb.argsparser.ArgsParser()
		pb.errorhandler.initializing += 1
		argsParser.readUserArgs(sys.argv)
		pb.errorhandler.last_error()
		pb.errorhandler.initializing -= 1
		argsParser.readUserArgs(args)
		requestedOp = argsParser.getRequestedOperation()
		if requestedOp is None:
			self.out('Invalid operation')
			return
		if requestedOp[0] == '@':
			helper = pb.helper.Helper()
			pb.argsparser.ArgsParser.operations[requestedOp]['api'](helper)
			return
		if not argsParser.isAuthenticated():
			self.out('Missing authentication')
			return
		formatter = pb.formatter.Formatter()
		if argsParser.baseArgs['s']:
			formatter.shortFormat()
		api = pb.api.API(argsParser.baseArgs['u'], argsParser.baseArgs['p'], debug = argsParser.baseArgs['debug'])
		if pb.errorhandler.last_error() != 0:
			return
		apiResult = pb.argsparser.ArgsParser.operations[requestedOp]['api'](api, argsParser.opArgs)
		if pb.errorhandler.last_error() != 0:
			return
		try:
			pb.argsparser.ArgsParser.operations[requestedOp]['out'](formatter, apiResult)
		except Exception as e:
			self.out('ERROR: Internal error while printing response')
			self.out('-');
			return
		
		while self.wait and self.default_dc is not None:
			if self.default_dc_state(api) == 'AVAILABLE' or pb.errorhandler.last_error() != 0:
				break
			sys.stdout.write('.')
			sys.stdout.flush()
			time.sleep(1)
		if (self.wait):
			self.out('\n')
		self.out('-')

	def parse(self, text):
		args = shlex.split(text)
		if len(args) == 0:
			return
		cmd = args[0]
		
		# find command and run if internal (@list, @list-simple)
		if cmd in self.cmds_internal:
			self.cmds_internal[cmd](args[1:])
			self.out('')
			return
		
		# add default datacenter at position 1 (so command stays first and all other arguments follow -dcid)
		if self.default_dc is not None:
			args.insert(1, '-dcid')
			args.insert(2, self.default_dc)
		
		# find command
		for c in self.cmds_api:
			if c.replace('-', '').replace('@', '').lower() == cmd.replace('-', '').replace('@', '').lower():
				self.run_command(c, args)
				return
		
		spellcheck = pb.spellcheck.SpellCheck([i.lower() for i in self.cmds_api])
		match = spellcheck.one_match(cmd)
		if match is None:
			self.out('Unknown command "%s"' % cmd)
			self.do_about()
		else:
			self.out('Unknown command, interpreting "%s" as "%s"' % (cmd, match))
			args[0] = match
			self.run_command(match.replace('-', '').replace('@', '').lower(), args)

	def default_dc_state(self, api):
		return api.getDataCenterState(self.default_dc)

	def start(self):
		readline.set_completer(self.completer())
		readline.parse_and_bind('tab: menu-complete')
		readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))
		self.do_about()
		self.out('')
		self.parse('get-all-datacenters')
		while True:
			try:
				text = raw_input(self.prompt())
			except:
				self.out('')
				self.do_exit()
			self.parse(text)

	def do_about(self):
		self.out('')
		self.out(self.tbold + 'ProfitBricks API CLI v' + self.version + ' Copyright 2012 ProfitBricks GmbH' + self.treset + ', licensed under Apache 2.0 ( http://www.apache.org/licenses/LICENSE-2.0 )')
		self.out("Type 'exit' to leave, 'help' for help, 'list' to list available operations, 'use DatacenterId' to set a default working datacenter.")

	def do_help(self):
		self.do_about()
		if platform.system() == 'Linux':
			os.system('man -l pbapi.1')
		else:
			self.out('')
			self.out('Unknown operating system. If your operating system can read Unix manual pages, open the file \'pbapi.1\'.')

	def do_use(self, args):
		if len(args) == 0:
			self.default_dc = None
			return
		if args[0].isdigit() and int(args[0]) <= len(pb.api.API.datacenters) and int(args[0]) >= 1:
			self.default_dc = str(pb.api.API.datacenters[int(args[0]) - 1].dataCenterId) # we count from 1, array is from 0
		else:
			self.default_dc = args[0] if len(args) > 0 else None
		found = False
		for dc in pb.api.API.datacenters:
			if self.default_dc == dc.dataCenterId:
				found = True
		if not found:
			self.default_dc = None
		print "Default datacenter:", (self.default_dc if self.default_dc is not None else "none")
		if self.default_dc is not None:
			self.parse('get-datacenter -s')

	def do_exit(self):
		self.out('Bye!')
		sys.exit(0)

	def do_wait(self):
		self.out('All operations will wait for data center to become available')
		self.wait = True

	def do_nowait(self):
		self.out('All operations will immediately return control to the user without waiting for provisioning')
		self.wait = False

	def do_nothing(self):
		pass

def restart_program(msg = None):
	# Restarts the current program.
	# Note: this function does not return. Any cleanup action (like
	# saving data) must be done before calling this function.
	if msg is not None:
		print msg
	sys.stdout.flush()
	python = sys.executable
	os.execl(python, python, * sys.argv)

def auth_update():
	print "Checking for updates: ",
	system=platform.system()
	if system == 'Linux':
		if os.path.isfile('./update.sh'):
			sys.stdout.flush()
			exit_code = os.system('./update.sh')
			return (exit_code > 0)
		else:
			print "Updater not found, skpping."
	else:
		print "Can only update on Linux systems (found: " + system + ")."
	return False

if auth_update():
	restart_program('The API has been updated and the application will now restart.')

shell = Shell()
shell.start()

