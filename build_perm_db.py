import os
import re
import socket
import sys
import time
import datetime
import sqlite3
from db_work import *


db_name = "Current_network_db.db"
#If you make changes here to sure and make changes in explore the network table_dics
tables_columns = [
	{'table': 'cdp',
		'columns':[['deviceId', 'VARCHAR(200)'],
		['ipAddress' ,'VARCHAR(200)'],
		['platform',  'text'],
		['capabilities',  'text'],
		['localInterface',  'VARCHAR(200)'],
		['interface',  'VARCHAR(200)'],
		['version', 'text'],
		['vtpDomain', 'text'],
		['nativeVlan', 'text'],
		['duplex',  'text'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],],
	'primary_key':'deviceId,ipAddress,localInterface,interface,local_host'},
	 
	{'table': 'ospf',
		'columns':[['address' ,'VARCHAR(200)'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],
		[ 'interface' ,'VARCHAR(200)'],
		[ 'neighbor_id' ,'VARCHAR(200)'],
		[ 'state','VARCHAR(200)'],],
	'primary_key':'local_host, address, interface, neighbor_id, state'},

	{'table': 'inventory',
		'columns':[['descr','VARCHAR(200)'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],
		[ 'name','VARCHAR(200)'],
		[ 'pid','VARCHAR(200)'],
		[ 'sn','VARCHAR(200)'],],
	#'primary_key':'local_host, descr, name, pid,sn'
	},
	
	{'table': 'connected_subnets',
		'columns':[['nexthop_if','VARCHAR(200)'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],
		['network','VARCHAR(200)'],
		['mask','VARCHAR(200)'],],
	'primary_key':'local_host, network, mask, nexthop_if'},		
	
	{'table': 'bgp',
		'columns':[['bgp_neigh','VARCHAR(200)'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],
		['neigh_as' ,'VARCHAR(200)'],],
	'primary_key':'local_host, bgp_neigh, neigh_as'},	
	
	{'table': 'ip_int_brief',
		'columns':[['intf','VARCHAR(200)'],
		[ 'local_host','VARCHAR(200)'],
		[ 'dls','text'],
		[ 'dau','text'],
		 ['ipaddr'  ,'VARCHAR(200)'],],
	'primary_key':'local_host, intf, ipaddr'},

	{'table': 'raw_data',
		'columns':[['show_run','text'],
		[ 'local_host','text'],
		[ 'dls','text'],
		[ 'dau','text'],],
	#'primary_key':'local_host, show_run'
	},

	{'table': 'show_ver',
		'columns':[['version','text'],
		['uptime','text'],
		['running_image','text'],
		[ 'local_host','VARCHAR(200)'],
		[ 'config_register','text'],
		[ 'dls','text'],
		[ 'dau','text'],],
	'primary_key':'local_host'}

	 ]
	
build_db(db_name,tables_columns)