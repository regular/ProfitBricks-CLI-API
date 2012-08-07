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

#
# EXAMPLE FILE FOR PROFITBRICKS CUSOMTERS AND DEVELOPERS
#
# This file is an example showing you how to use the the client proxy (in src/pb/client.py) 
# to send request to Profitbricks API from Python. Copy the 'pb/client.py' file in your working directory,
# import it in your app (import client) and follow the examples shown
# below. If you still need help, contact support@profitbricks.com
#

# The following example demonstrates the ability to freely update your desired data center anytime
# create a data center with
# - 1 load balancer lb and 2 balanced servers lbs1 and lbs2 on lan 1
# - lan 1 has internet access
# - server s2 on public lan 1
# - server s3 connect to s2 on private lan 2
# - create a storage and connect to s3, if there is a test image available
#
# @author tri.vohoang

import sys
import time
import pb.client
import pb.formatter

# authentication here
username = "test"
password = "test"

# init client proxy
proxy = pb.client.ClientProxy(username, password, True)

# create a dc
import random
new_dc_name = 'DC_EXAMPLE_' + str(random.randrange(1000, 9999))

print 'Creating new data center named "%s"' % new_dc_name
dcid = proxy.createDataCenter(new_dc_name).dataCenterId

print 'New data center ID is %s' % dcid
print ''

# now create lbs1, lbs2 on a new lan 1. Lan 1 is implicitly created and public to internet
createServerRequest = {'cores': 1, 'ram': 256, 'dataCenterId': dcid, 'lanId': 1, 'internetAccess': True}

# create lbs1
createServerRequest['serverName'] = 'lbs1'
lbs1_id = proxy.createServer(createServerRequest).serverId
print 'Server lbs1 is created on lan 1 with id "%s"' % lbs1_id

# create lbs2
createServerRequest['serverName'] = 'lbs2'
lbs2_id = proxy.createServer(createServerRequest).serverId
print 'Server lbs2 is created on lan 1 with id "%s"' % lbs2_id

# create lb on lan 1, with balanced server lbs1
createLbRequest = {'dataCenterId': dcid, 'loadBalancerName': 'lb', 'lanId': 1, 'serverIds': [lbs1_id]}
lbid = proxy.createLoadBalancer(createLbRequest).loadBalancerId
print 'Load balancer lb is created on lan 1 with balancer server lbs2 with id "%s"' % lbid

# you can also register server lbs2 with load balancer later
proxy.registerServersOnLoadBalancer([lbs2_id], lbid)
print 'Server lbs2 is registered with lb'

# create server s2 on lan 1
createServerRequest['serverName'] = 's2'
# Lan 1 was already created before. You can connect to it but cannot set Lan to public or private. This setting is ignored
createServerRequest['internetAccess'] = False
s2_id = proxy.createServer(createServerRequest).serverId
print 'Server s3 is created on lan 1 with id "%s"' % s2_id

# create server s3 on new lan 2. Lan 2 is implicitly created
createServerRequest['serverName'] = 's3'
createServerRequest['lanId'] = 2
s3_id = proxy.createServer(createServerRequest).serverId
print 'Server s3 is created on lan 2 with id "%s"' % s3_id

# create nic on s2 and connect to lan 2. Lan 2 is implicitly created
createNicRequest = {'serverId': s2_id, 'lanId': 2}
nic_s2_id = proxy.createNic(createNicRequest).nicId
print 'A nic is created on s2, connect to Lan 2 with id "%s"' % nic_s2_id

# feel free to turn a Lan to public or private
print 'Turn Lan 2 public...'
proxy.setInternetAccess(dcid, 2, True)
print 'Turn Lan 2 private...'
proxy.setInternetAccess(dcid, 2, False)

# request storage sto, size 1GiB
createStorageRequest = {'size': 1, 'dataCenterId': dcid, 'storageName': 'sto'}

# find a test HDD image smaller than 1Gb
images = proxy.getAllImages()
for image in images:
	if image['imageType'] == 'HDD' and image['imageSize'] < 1000 and image['region'] == 'EUROPE':
		print 'Found a testing HDD image "%s"' % image['imageId']
		createStorageRequest['mountImageId'] = image['imageId']
		break

# now create storage
sto_id = proxy.createStorage(createStorageRequest).storageId
print 'Storage created with id "%s"' % sto_id

# connect sto to s3
connectStorageRequest = {'storageId': sto_id, 'serverId': s3_id}
proxy.connectStorageToServer(connectStorageRequest)
print 'Storage sto is connected to s3'

# your requests are submited, now you can wait for provisioning to complete
print "waiting for provisioning to complete"
wait = 0
state = ''
while(True):
	wait +=1
	print ".",
	if wait == 50:
		print "Provisioning timeout after 5 minutes"
		break
	state = proxy.getDataCenterState(dcid)
	if state == 'AVAILABLE':
		break
	else:
		time.sleep(6)

if(state == 'AVAILABLE'):
	dc = proxy.getDataCenter(dcid)
	formatter = pb.formatter.Formatter()
	formatter.printDataCenter(dc)