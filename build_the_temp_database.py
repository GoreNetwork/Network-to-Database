import os
from getpass import getpass
import re
from pprint import pprint
from db_work import *
import time




#This builds a set of tables from a dictionariy

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


#Regular expressoin to find IP addresses
def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

def read_doc (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc

def read_in_ips():
	ips_doc = "IPs.txt"
	ips = []
	for line in read_doc (ips_doc):
		temp_ips = get_ip (line)
		for temp_ip in temp_ips:
			ips.append(temp_ip)
	return ips

#main function that ties everything together

def build_to_do_database(table_dics):
	db_name = table_dics['tmp_db']["db_name"]
	
	#Table Structure
	#If you make changes here to sure and make changes in explore the network table_dics
	tables_columns = [
			{
			'table': 'to_do_ips',
			'columns':[['ip','text']],
			'primary_key':'ip'},
			{
			'table': 'done',
			'columns':[['ip','text']]},
			{'table': 'issues',
			'columns':[['ip','text']],
			'primary_key':'ip'},
		]


	#Pull in IPs from the IPs document
	ips = read_in_ips()
	#Build the DB from the structure above
	#build_db(db_name,tables_columns)
	#Put the IPs into the to_do_ips table
	build_table_commands = [
	"DROP TABLE IF EXISTS to_do_ips",
	"DROP TABLE IF EXISTS done",
	"DROP TABLE IF EXISTS issues",
	"CREATE TABLE to_do_ips(ip varchar(39) unique);",
	"CREATE TABLE done(ip varchar(39) unique);",
	"CREATE TABLE issues(ip varchar(39) unique);",
	]
	conn = MySQLdb.connect(db_location,db_user, db_password,temp_db)
	cur = conn.cursor()
	for build_table_command in build_table_commands:
		cur.execute(build_table_command)
	conn.commit()
	cur.close
	conn.close
	put_ips_in_todo_db(table_dics,ips)

#Name of Database that will be created
db_name = 'temp.db'

def pull_all_table_data(conn,cur,table):
	command = 'select * from {};'.format(table)
	returned_data = cur.execute(command)
	return returned_data.fetchall()

def pull_ip(tmp_db_dic):
	conn = MySQLdb.connect(db_location,db_user, db_password,temp_db)
	cur = conn.cursor()
	output = []
	remove_from_table = tmp_db_dic['to_do_table']
	add_to_table = tmp_db_dic['done_table']
	good_ip = False
	while good_ip == False:
		command = "SELECT ip FROM {} order by rand() limit 1;".format(remove_from_table)
		cur.execute(command)
		ip_to_do = cur.fetchall()
		if (len(ip_to_do)) == 0:
			return "Done"
		if len(ip_to_do[0][0]) == 0:
			print (ip_to_do, 'build temp db line 107 when this is nothing the program has reached the end of the DB and crashes, that means it is done')
		ip = ip_to_do[0][0]
		command = "select ip from {} where (ip = '{}');".format (add_to_table,ip)
		cur.execute(command)
		done_ips = cur.fetchall()
		if len(done_ips) == 0:
			good_ip = True
		command = "DELETE FROM {} where (ip ='{}');".format(remove_from_table,ip)
		cur.execute(command)
		conn.commit()
		time.sleep(.1)
	cur.close
	conn.close
	insert_into_done(ip,tmp_db_dic )
	return ip



def insert_ip_into_issues(db_name,ip):
	conn = MySQLdb.connect(db_location,db_user, db_password,temp_db)
	cur = conn.cursor()
	issues_table = 'issues'
	command = "INSERT INTO {} ('ip') VALUES('{}')".format(issues_table,ip)
	try:
		returned_data = cur.execute(command)
	except Exception as e: 
		if "UNIQUE constraint failed" not in str(e):
			if 'Duplicate entry' not in str(e):
				print ('build_temp line 135',str(e))

				
	command = 'select * from {};'.format(issues_table)
	returned_data = cur.execute(command)
	conn.commit()
	cur.close
	conn.close

def insert_into_done(ip,tmp_db_dic):
	db_name = tmp_db_dic['db_name']
	add_to_table = tmp_db_dic['done_table']
	conn = MySQLdb.connect(db_location,db_user, db_password,temp_db)
	cur = conn.cursor()
	command = "INSERT INTO {} (ip) VALUES('{}');".format(add_to_table,ip)
	try:
		cur.execute(command)
	except Exception as e: 
		if "UNIQUE constraint failed" not in str(e):
			if 'Duplicate entry' not in str(e):
				print ('build_temp line 155',str(e))
	conn.commit()
	cur.close
	conn.close
