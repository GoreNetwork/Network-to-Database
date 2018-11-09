import sqlite3
import random
from pprint import pprint





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

def build_db(db_name,tables_columns):
	conn = sqlite3.connect(db_name)
	cur = conn.cursor()
	for table_column in tables_columns:
		cur.execute("DROP TABLE IF EXISTS {}".format (table_column['table']))
		SQL_statment = "CREATE TABLE {}(".format (table_column['table'])
		for column in table_column['columns']:
			SQL_statment = SQL_statment+column[0]+ " "+column[1]+","
		SQL_statment = SQL_statment[:-1]
		SQL_statment = SQL_statment+')'
		print (SQL_statment )
		cur.execute (SQL_statment)
	conn.commit()
	cur.close
	conn.close

def enter_info_into_db_specific(done_device,cur,conn):
	today = date.today()
	cur.execute("INSERT INTO devices (site_name,show_run,ip_int_brief,BGP_nei,OSFP_nei,EIGRP_nei,CDP_nei,int_status,updated) VALUES(?,?,?,?,?,?,?,?,?)",
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


def insert_into_test_table(d1,d2,ip,key,cur,conn):
	cur.execute("INSERT INTO test_table ('test_data_1','test_data_2','ip','key') VALUES(?,?,?,?)",
		(d1,d2,ip,key))
	conn.commit()


test_tables_datas = [
['test_data_1','1st data'],
['test_data_2', '2st data'],
['ip','192.168.0.1'],
['key','1'],
]


database = "test.db"

table = [
		{
		'table': 'test_table',
		'columns':[
			['test_data_1','text'],
			['test_data_2','text'],
			['ip','text'],
			['key','text primary key'],
				]
		}
	]
#build_db(database,table)
conn = sqlite3.connect(database)
cur = conn.cursor()
d1 = 'data3'
d2 = 'data4'
ip = '192.168.0.2'
key = '2'

#def turn_sql_return_into_list


def get_and_delete_row_of_test_table(conn,cur):
	output = []
	command = "SELECT key,ip FROM test_table order by random() limit 1;"
	returned_data = cur.execute(command)
	row = returned_data.fetchall()[0]
	key = row[0]
	ip = row[1]
	command = 'delete from test_table where key = "{}";'.format(key)
	returned_data = cur.execute(command)
	print('retreved data ',row)
	command = 'select * from test_table;'
	returned_data = cur.execute(command)
	print('all data',returned_data.fetchall())

conn.commit()

perm_db_name = "Current_network_db.db"

conn = sqlite3.connect(perm_db_name)
cur = conn.cursor()
command = 'select * from cdp where local_host = "oh-brecon-me3400-sonet-1"'
returned_data = cur.execute(command)
for each in returned_data:
	print (each)
cur.close
conn.close




conn.commit()