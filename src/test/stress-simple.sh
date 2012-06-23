#!/bin/bash

name='test-2'

function api() {
	echo "# $@" >&2
	$(dirname $(readlink -f $0))/../pbapi.py $@ | grep -v 'Request ID'
}

function api_id() {
	api $@ | grep 'ID:' | sed -e 's/.*ID: //'
}

echo '-'
dc=$(api_id create-data-center -name ${name})
echo DC: ${dc}
echo '-'

srv1=$(api_id create-server -name srv1 -dcid ${dc} -cores 1 -ram 256 -lanid 99 -internetaccess y)
echo "SRV 1: ${srv1}"
api create-nic -srvid ${srv1} -lanid 1 -name srv1-nic2
api create-nic -srvid ${srv1} -lanid 2 -name srv1-nic3
api create-nic -srvid ${srv1} -lanid 5 -name srv1-nic4

srv2=$(api_id create-server -name srv2 -dcid ${dc} -cores 1 -ram 256 -lanid 99)
echo "SRV 2: ${srv2}"
api create-nic -srvid ${srv2} -lanid 1 -name srv2-nic2
api create-nic -srvid ${srv2} -lanid 2 -name srv2-nic3
api create-nic -srvid ${srv2} -lanid 5 -name srv2-nic4

srv3=$(api_id create-server -name srv3 -dcid ${dc} -cores 1 -ram 256)
echo "SRV 3: ${srv3}"
api create-nic -srvid ${srv3} -lanid 2 -name srv3-nic1
api create-nic -srvid ${srv3} -lanid 3 -name srv3-nic2

srv4=$(api_id create-server -name srv4 -dcid ${dc} -cores 1 -ram 256)
echo "SRV 4: ${srv4}"
api create-nic -srvid ${srv4} -lanid 2 -name srv4-nic1
api create-nic -srvid ${srv4} -lanid 3 -name srv4-nic2
api create-nic -srvid ${srv4} -lanid 4 -name srv4-nic3

srv5=$(api_id create-server -name srv5 -dcid ${dc} -cores 1 -ram 256)
echo "SRV 5: ${srv5}"
api create-nic -srvid ${srv5} -lanid 2 -name srv5-nic1
api create-nic -srvid ${srv5} -lanid 4 -name srv5-nic2

stoid=$(api_id create-storage -size 1 -name srv1-sto1 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv1} -bus ide

stoid=$(api_id create-storage -size 1 -name srv2-sto1 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv2} -bus ide

stoid=$(api_id create-storage -size 1 -name srv3-sto1 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv3} -bus ide

stoid=$(api_id create-storage -size 1 -name srv4-sto1 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv4} -bus ide

stoid=$(api_id create-storage -size 1 -name srv4-sto2 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv4} -bus ide

stoid=$(api_id create-storage -size 1 -name srv4-sto3 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv4} -bus ide

stoid=$(api_id create-storage -size 1 -name srv5-sto1 -dcid ${dc})
echo "STO: ${stoid}"
api connect-storage-to-server -stoid ${stoid} -srvid ${srv5} -bus ide

while [ 1 ]; do
	( api get-datacenter-state -dcid ${dc} | grep 'AVAILABLE' ) && break
	sleep 1
	echo '.'
done

