import os
import re
import socket
import sys
import time
import datetime
#import sqlite3
import MySQLdb
from common_functions import *
from pprint import pprint

#There are 2 of these, 1 in explore

#This builds a set of tables from a dictionariy

#1st state the name
#db_name = 'test.db'

#Next is a list of list of directories, "table" is the table name
#columnts is a list [0] is the feild name [1] is the feild type
#tables_columns = [{'table': "devices_subnets",
#'columns':[['device_id','TEXT'],['interface','TEXT'],['ip','TEXT'],['subnet_mask','TEXT']]},
#
#{'table': "devices_ipv4_routing",
#'columns':[['device_id','TEXT'],['OSPF_config','TEXT'],['BGP_config','TEXT'],['route_map','TEXT'],['prefix_list','TEXT'],['redist_connected','TEXT']]},
#]

#Next we call the function below
#build_db(db_name,tables_columns)

db_location = "localhost"
db_user = 'root'
db_password = 'password'
perm_db = 'network_data_db'
temp_db = 'temp_db'

def build_db(db_name,tables_columns):
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for table_column in tables_columns:
		cur.execute("DROP TABLE IF EXISTS {}".format (table_column['table']))
		SQL_statment = "CREATE TABLE {}(".format (table_column['table'])
		for column in table_column['columns']:
			SQL_statment = SQL_statment+column[0]+ " "+column[1]+","
		SQL_statment = SQL_statment[:-1]
		
		if 'primary_key' in table_column:
			SQL_statment = SQL_statment+','+'PRIMARY KEY({})'.format(table_column['primary_key'])
		SQL_statment = SQL_statment+')'
		print ("SQL Statment:\n\n", SQL_statment,'\n\n\n')
		cur.execute (SQL_statment)
		
	conn.commit()
	cur.close
	conn.close

def enter_info_into_db(done_device,cur,conn):
	today = date.today()
	cur.execute("""INSERT INTO devices (site_name,show_run,ip_int_brief,BGP_nei,OSFP_nei,EIGRP_nei,CDP_nei,int_status,updated) 
	VALUES(?,?,?,?,?,?,?,?,?)
	ON DUPLICATE KEY UPDATE
	site_name=VALUES(site_nam),
	show_run=VALUES(show_run),
	ip_int_brief=VALUES(ip_int_brie),
	BGP_nei=VALUES(BGP_nei),
	OSFP_nei=VALUES(OSFP_nei),
	EIGRP_nei=VALUES(EIGRP_nei),
	CDP_nei=VALUES(CDP_nei),
	int_status=VALUES(int_status),
	updated=VALUESupdated(),

	
	""",
		(done_device['site_name'],
		done_device['run'],
		done_device['int_brief'],
		done_device['bgp'],
		done_device['ospf'],
		done_device['eigrp'],
		done_device['cdp'],
		done_device['int_status'],
		today
		))
	conn.commit()

def put_ips_in_todo_db(table_dics,ips):
	db_name = table_dics['tmp_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, temp_db)
	cur = conn.cursor()
	for ip in ips:
		command = "INSERT INTO {} (ip) VALUES(%s)".format(table_dics['tmp_db']['to_do_table'])
		try:
			data = (ip)
			cur.execute(command , (ip,))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ("IPs into To Do", str(e))
				pass
	#command = 'select * from {};'.format(table_dics['tmp_db']['to_do_table'])
	#returned_data = cur.execute(command)
	conn.commit()
	cur.close
	conn.close

def put_cdp_data_in_db(cdp_data,table_dics):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()	
	keys = ['capabilities',
			'local_host',
			'dls',
			'dau',
			'deviceId',
			'duplex',
			'interface',
			'ipAddress',
			'localInterface',
			'platform',
			'version']
	for key in keys:
		if key not in cdp_data:
			cdp_data[key] = None

	command = """INSERT INTO {} (capabilities, local_host, dls, dau, deviceid, duplex, interface, ipaddress, localinterface,  platform, version) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
	ON DUPLICATE KEY UPDATE
	capabilities=VALUES(capabilities), 
	dls=VALUES(dls),
	dau=VALUES(dau),
	deviceid=VALUES(deviceid),
	duplex=VALUES(duplex),
	interface=VALUES(interface),
	ipaddress=VALUES(ipaddress),
	localinterface=VALUES(localinterface),
	platform=VALUES(platform),
	version=VALUES(version)	""".format(table_dics['perm_db']['cdp'])
	try:
		cur.execute(command,
			(cdp_data['capabilities'],
			cdp_data['local_host'],
			cdp_data['dls'],
			cdp_data['dau'],
			cdp_data['deviceId'],
			cdp_data['duplex'],
			cdp_data['interface'],
			cdp_data['ipAddress'],
			cdp_data['localInterface'],
			cdp_data['platform'],
			cdp_data['version']))
	except Exception as e: 
		if "Duplicate entry" not in str(e):
			print ('CDP', str(e))
	
	conn.commit()
	cur.close
	conn.close
	
def insert_into_ip_int_brief(ip_dic,table_dics):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()	
	command = """INSERT INTO {} (intf,local_host, dls, dau, ipaddr) values (%s,%s,%s,%s,%s)
	ON DUPLICATE KEY UPDATE
	intf=VALUES(intf),
	local_host=VALUES(local_host),
	dls=VALUES(dls),
	dau=VALUES(dau),
	ipaddr=VALUES(ipaddr)
	;""".format(table_dics['perm_db']['ip_brief'])
	try:
		cur.execute(command,(
			ip_dic['intf'],
			ip_dic['local_host'],
			ip_dic['dls'],
			ip_dic['dau'],
			ip_dic['ipaddr']))
	except Exception as e: 
		if "Duplicate entry" not in str(e):
			print ('IP int brief',str(e))
	conn.commit()
	cur.close
	conn.close

def insert_into_ospf(table_dics,ospf_data,current_data ):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for ospf_entry in ospf_data:
		ospf_entry =  merge_dics(current_data,ospf_entry)
		ips = [ospf_entry['neighbor_id']]
		put_ips_in_todo_db(table_dics, ips)
		command = """INSERT INTO {} (address, local_host, dls, dau, interface, neighbor_id, state) values (%s,%s,%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE
		address=VALUES(address), 
		local_host=VALUES(local_host), 
		dls=VALUES(dls),
		dau=VALUES(dau),
		interface=VALUES(interface), 
		neighbor_id=VALUES(neighbor_id), 
		state=VALUES(state)

		;""".format(table_dics['perm_db']['ospf'])
		try:
			cur.execute(command,(
				ospf_entry['address'],
				ospf_entry['local_host'],
				ospf_entry['dls'],
				ospf_entry['dau'],
				ospf_entry['interface'],
				ospf_entry['neighbor_id'],
				ospf_entry['state']))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ("OSPF", str(e))
	conn.commit()
	cur.close
	conn.close

def insert_into_inv(table_dics,inv,current_data ):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for device in inv:
		device =  merge_dics(current_data,device)
		command = """INSERT INTO {} (descr, local_host, dls, dau, name, pid, sn) values(%s,%s,%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE
		local_host=VALUES(local_host), 
		dls=VALUES(dls),
		dau=VALUES(dau),
		descr=VALUES(descr), 
		name=VALUES(name), 
		pid=VALUES(pid), 
		sn=VALUES(sn)
		;""".format(table_dics['perm_db']['inventory'])
		try:
			cur.execute(command,(
				device['descr'],
				device['local_host'],
				device['dls'],
				device['dau'],
				device['name'],
				device['pid'],
				device['sn']))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ('inv',str(e))		
	conn.commit()
	cur.close
	conn.close

def insert_into_connected_subnets(table_dics,subnets,current_data):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for subnet in subnets:
		subnet = merge_dics(current_data,subnet)
		command = """INSERT INTO {} (nexthop_if, local_host, dls, dau, network, mask) values(%s,%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE
		local_host=VALUES(local_host), 
		dls=VALUES(dls),
		dau=VALUES(dau),
		nexthop_if=VALUES(nexthop_if),
		network=VALUES(network),
		mask=VALUES(mask)
		""".format(table_dics['perm_db']['connected_subnets'])
		try:
			cur.execute(command,(
				subnet['nexthop_if'],
				subnet['local_host'],
				subnet['dls'],
				subnet['dau'],
				subnet['network'],
				subnet['mask']))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ('Conn_subnet',str(e))			
	conn.commit()
	cur.close
	conn.close

def insert_into_bgp(table_dics,bgp_neighbors,current_data):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for neighbor in bgp_neighbors:
		neighbor = merge_dics(current_data,neighbor)
		command = """INSERT INTO {} (bgp_neigh, local_host, dls, dau, neigh_as) values(%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE
		local_host=VALUES(local_host), 
		dls=VALUES(dls),
		dau=VALUES(dau),
		bgp_neigh=VALUES(bgp_neigh),
		neigh_as=VALUES(neigh_as)
		
		""".format(table_dics['perm_db']['bgp'])
		try:
			cur.execute(command,(
				neighbor['bgp_neigh'],
				neighbor['local_host'],
				neighbor['dls'],
				neighbor['dau'],
				neighbor['neigh_as']))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ('BGP',str(e))
	conn.commit()
	cur.close
	conn.close

def insert_into_raw_data(table_dics,raw_commands,current_data):
	raw_commands = merge_dics(current_data,raw_commands)
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	
	command = """INSERT INTO {} (show_run, local_host, dls, dau) values (%s,%s,%s,%s)""".format(table_dics['perm_db']['raw_data'])
	try:
		cur.execute(command,(
			raw_commands['show_run'],
			raw_commands['local_host'],
			raw_commands['dls'],
			raw_commands['dau'],))
	except Exception as e: 
		if "Duplicate entry" not in str(e):
			print ('RAW', str(e))			
	conn.commit()
	cur.close
	conn.close


def insert_into_show_ver(table_dics,show_vers,current_data):
	perm_db_name = table_dics['perm_db']['db_name']
	conn = MySQLdb.connect(db_location, db_user, db_password, perm_db)
	cur = conn.cursor()
	for show_ver in show_vers:
		show_ver = merge_dics(current_data,show_ver)
		command = """INSERT INTO {} (version, uptime, running_image, local_host, config_register,dls,dau) values (%s,%s,%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE
		local_host=VALUES(local_host), 
		dls=VALUES(dls),
		dau=VALUES(dau),		
		version=VALUES(version),
		uptime=VALUES(uptime),
		running_image=VALUES(running_image),
		config_register=VALUES(config_register)
		""".format(table_dics['perm_db']['show_ver'])
		try:
			cur.execute(command,(
				show_ver['version'],
				show_ver['uptime'],
				show_ver['running_image'],
				show_ver['local_host'],
				show_ver['config_register'],
				show_ver['dls'],
				show_ver['dau'],))
		except Exception as e: 
			if "Duplicate entry" not in str(e):
				print ('show_ver',str(e))
	conn.commit()
	cur.close
	conn.close