#!/usr/bin/python

#
# v1.2.2 Copyright 2012 ProfitBricks GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

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
#import pb.spellcheck

class Shell:

     version = '1.2.2'

     cmds_internal = {}
     cmds_api = pb.argsparser.ArgsParser().operations
     tbold = '\033[1m'
     treset = '\033[0;0m'

     default_dc = None
     wait = False

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
          pb.formatter.Formatter.out = temp_out
          pb.errorhandler.initializing -= 1

     def out(self, text):
          pb.formatter.Formatter.out(pb.formatter.Formatter(), text)

     def prompt(self):
          return self.treset + '-\n' + self.tbold + ('ProfitBricks> ' if self.default_dc is None else self.default_dc + '> ') + self.treset

     def completer(self):
          this = self
          
          def inner_completer(text, state):
               clean_text = this.clean_cmd(text)
               is_first_word = text == readline.get_line_buffer()
               if clean_text == '' and is_first_word:
                    print ''
                    this.do_about()
                    sys.stdout.write(this.prompt() + readline.get_line_buffer())
                    return None
               matches = []
               
               if is_first_word:
                    # if first word on readline, internal commands and api commands
                    for cmd in this.cmds_internal:
                         if this.clean_cmd(cmd).startswith(clean_text):
                              matches.append('@' + pb.helper.Helper.camelCaseToDash(cmd))
                    for cmd in this.cmds_api:
                         if this.clean_cmd(cmd).startswith(clean_text):
                              matches.append(pb.helper.Helper.camelCaseToDash(cmd))
               else:
                    # if not first word in readline, data center ids and server ids
                    for dc in pb.api.API.datacenters:
                         if this.clean_cmd(dc.dataCenterId).startswith(clean_text):
                              matches.append(dc.dataCenterId)
               
               matches.sort()
               
               # no matches?
               if state >= len(matches):
                    return None
               
               # cut to longest common beginning
               common = matches[0].replace('@', '')
               for m in matches:
                    if m[0 : 1] == '@':
                         m = m[1 : ]
                         j = 1
                    else:
                         j = 0
                    internal_pos_adjust = j
                    while j < len(common):
                         if j >= len(m):
                              common = common[0 : j - 1 + internal_pos_adjust]
                              break
                         if m[j] != common[j]:
                              common = common[0 : j + internal_pos_adjust]
                              break
                         j += 1
               
               # if there are no matches, avoid printing all autocomplete possibilities
               if common == '':
                    return None
               
               # quote if we have spaces
               if common.find(' ') != -1:
                    common = "'" + common + "'"
               
               # if more than one match, and first Tab autocomplete request, print possibilities and the prompt again
               if (len(matches) > 1) and (state == 0):
                    print ''
                    for m in matches:
                         print m
                    sys.stdout.write(this.prompt() + readline.get_line_buffer())
               
               # we had exactly one match, return it along with a trailing whitespace
               return (common + ' ' if len(matches) == 1 else matches[state] + ' ')
          
          return inner_completer

     def run_command(self, cmd, args):
          if cmd == 'deletedatacenter':
               if self.default_dc is not None:
                    self.out('Data center ' + self.default_dc + ' is in use. You may not perform any data center deletion operations. Type \'use\' to reset and try again\n')
                    return
          args.insert(0, 'pbapi-internal-placeholder-text') # equivalent of argv[0]
          argsParser = pb.argsparser.ArgsParser()
          pb.errorhandler.initializing += 1
          argsParser.readUserArgs(sys.argv)
          pb.errorhandler.last_error()
          pb.errorhandler.initializing -= 1
          argsParser.readUserArgs(args)
          requestedOp = argsParser.getRequestedOperation()
          if requestedOp == '':
               # argsParser is telling us to ignore this command
               # this hack will be removed once we replace errorhandler with exceptions
               return
          if requestedOp is None:
               raise Exception('Invalid operation')
          if requestedOp[0] == '@':
               helper = pb.helper.Helper()
               pb.argsparser.ArgsParser.operations[requestedOp]['api'](helper)
               return
          if not argsParser.isAuthenticated():
               raise Exception('Authentication error: Missing authentication')
          formatter = pb.formatter.Formatter()
          if argsParser.baseArgs['s']:
               formatter.shortFormat()
          formatter.batch = argsParser.baseArgs["batch"]
          
          try:
               api = pb.api.API(argsParser.baseArgs['u'], argsParser.baseArgs['p'], debug = argsParser.baseArgs['debug'])
          except Exception as ex:
               self.out(str(ex));
               return
          
          if cmd == 'deletedatacenter':
               # check if datacenter is empty first (as per PB API 1.2 specs, clients should check if dc is empty before deleting)
               apiResult = pb.argsparser.ArgsParser.operations['getDataCenter']['api'](api, argsParser.opArgs)
               if ('servers' in apiResult and len(apiResult['servers']) > 0) or ('storages' in apiResult and len(apiResult['storages']) > 0) or ('loadBalancers' in apiResult and len(apiResult['loadBalancers']) > 0):
                    ans = raw_input('The data center is not empty! Do you want to continue? [y/N] ')
                    if ans[0:1].lower() != 'y':
                         self.out('Operation cancelled')
                         return
          
          apiResult = pb.argsparser.ArgsParser.operations[requestedOp]['api'](api, argsParser.opArgs)
          
          try:
               pb.argsparser.ArgsParser.operations[requestedOp]['out'](formatter, apiResult)
          except Exception as ex:
               raise Exception('Internal error while printing response: ' + str(ex))
               return
          
          self.waitOnce = argsParser.baseArgs["wait"] if ("wait" in argsParser.baseArgs and 'dcid' in argsParser.opArgs) else None
          while (self.wait and (self.default_dc is not None) and self.waitOnce is None) or (self.waitOnce is not None and self.waitOnce):
               try:
                    if (self.waitOnce is not None) and self.waitOnce:
                         try:
                              if api.getDataCenterState(argsParser.opArgs['dcid']) == 'AVAILABLE':
                                   break
                         except:
                              # data center may no longer be available in case of deleteDataCenter command
                              break
                    else:
                         if api.getDataCenterState(self.default_dc) == 'AVAILABLE':
                              break
               except Exception as ex:
                    self.out(str(ex))
                    break
               sys.stdout.write('.')
               sys.stdout.flush()
               time.sleep(1)
          self.waitOnce = None
          if (self.wait):
               self.out('\n')
          
          # reload datacenters list
          if cmd in ['createdatacenter', 'deletedatacenter']:
               try:
                    self.parse('get-all-datacenters')
               except Exception as ex:
                    raise Exception('Failed to get list of data centers: ' + str(ex))

     def clean_cmd(self, cmd):
          return cmd.replace('-', '').replace('@', '').lower();

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
          
          # add default data center at position 1 (so command stays first and all other arguments follow -dcid)
          if self.default_dc is not None:
               args.insert(1, '-dcid')
               args.insert(2, self.default_dc)
          
          # find and execute command if known to the API
          clean_cmd = self.clean_cmd(cmd)
          for c in self.cmds_api:
               if self.clean_cmd(c) == clean_cmd:
                    self.run_command(clean_cmd, args)
                    return
          
          #spellcheck = pb.spellcheck.SpellCheck([i.lower() for i in self.cmds_api])
          #match = spellcheck.one_match(cmd)
          match = None
          if match is None:
               self.out('Unknown command "%s"' % cmd)
               self.do_about()
          else:
               self.out('Unknown command, interpreting "%s" as "%s"' % (cmd, match))
               args[0] = match
               self.run_command(self.clean_cmd(match), args)

     def start(self):
          readline.set_completer(self.completer())
          readline.parse_and_bind('tab: menu-complete')
          readline.set_completer_delims(readline.get_completer_delims().replace('-', '')) # don't use '-' as separator
          self.do_about()
          try:
               self.parse('get-all-data-centers')
          except Exception as ex:
               self.out('Failed to get list of data centers: ' + str(ex))
          self.out('')
          while True:
               try:
                    text = raw_input(self.prompt())
               except:
                    self.out('')
                    self.do_exit()
               try:
                    self.parse(text)
               except Exception as ex:
                    self.out(str(ex))

     def do_about(self):
          self.out('')
          self.out(self.tbold + 'ProfitBricks API CLI v' + self.version + ' Copyright 2012 ProfitBricks GmbH' + self.treset + ', licensed under Apache 2.0 ( http://www.apache.org/licenses/LICENSE-2.0 )')
          self.out("Type 'exit' to leave, 'help' for help, 'list' to list available operations, 'use DatacenterId' to set a default working data center for the current CLI session.")

     def do_help(self):
          self.do_about()
          if platform.system() == 'Linux':
               manfile = os.path.dirname(__file__) + '/pbapi.1'
               os.system('man -l ' + manfile)
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
     print "Checking for updates (Ctrl+C to cancel): ",
     system=platform.system()
     if system == 'Linux':
          updater = os.path.dirname(__file__) + '/update.sh'
          if os.path.isfile(updater):
               sys.stdout.flush()
               exit_code = os.system(updater)
               if exit_code == 1:
                    return True
               if exit_code == 2:
                    print "Update cancelled"
               return False
          else:
               print "Updater not found, skpping."
     else:
          print "Can only update on Linux systems (found: " + system + ")."
     return False

if auth_update():
     restart_program('The API has been updated and the application will now restart.')

shell = Shell()
shell.start()

