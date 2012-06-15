#!/usr/bin/python

#
# v1.1.1 Copyright 2012 ProfitBricks GmbH
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

import pb.api
import sys

# configure
username = ''
password = ''

if username == '' or password == '':
	print 'Please configure the ProfitBricks username and password in the source file'
	sys.exit(1)

# connect
try:
	api = pb.api.API(username, password)
except Exception as e:
	print 'Error connecting to ProfitBricks: %s' % e.message
	sys.exit(2)
print 'We have connected to the ProfitBricks API'

# list data centers
print '[ List data centers ]'
dcs = api.getAllDataCenters()
for dc in dcs:
	print '%s => %s' % (dc.dataCenterId, dc.dataCenterName)
print ''

# create new data center
import random
new_dc_name = 'DATA CENTER EXAMPLE ' + str(random.randrange(1000, 9999))
print 'Creating new data center named "%s"' % new_dc_name
new_dc = api.createDataCenter(new_dc_name)
print 'New data center ID is %s' % new_dc.dataCenterId
print ''

# list data centers
print '[ List data centers ]'
dcs = api.getAllDataCenters()
for dc in dcs:
	print '%s => %s' % (dc.dataCenterId, dc.dataCenterName)
print ''

# delete data center
print 'Deleting the data center with id "%s"' % new_dc.dataCenterId
api.deleteDataCenter(new_dc.dataCenterId)
print ''

# list data centers
print '[ List data centers ]'
dcs = api.getAllDataCenters()
for dc in dcs:
	print '%s => %s' % (dc.dataCenterId, dc.dataCenterName)
print ''

