from orionsdk import SwisClient
from getpass import getpass
from pprint import pprint
import requests
import MySQLdb
import os
import datetime
import time
import calendar
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
#from common_functions import *
import smtplib
import email.message
import os

hostname = 'R1'
username = 'root'
password = "password"
location = "localhost"
database = 'network_data_db'

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()

def pull_cdp_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,deviceId,platform,capabilities,localInterface,interface,version from cdp where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def pull_inventory_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,descr,name,pid,sn from inventory where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def pull_int_brief_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,intf,ipaddr from ip_int_brief where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def pull_osfp_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,address,interface,neighbor_id,state from ospf where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)


def pull_show_ver_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,version,uptime,running_image,config_register from show_ver where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def pull_raw_data_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select show_run from raw_data where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def pull_subnet_data(hostname):
    output = []
    pprint (hostname)
    conn = MySQLdb.connect(location,username, password,database)
    command = "select local_host,nexthop_if,network,mask from connected_subnets where local_host ='{}';".format(hostname)
    cur = conn.cursor()
    cur.execute(command)
    deviceids_lists = cur.fetchall()
    for devices in deviceids_lists:
        output.append(devices)
    cur.close
    conn.close
    return (output)

def html_build_start_body():
    body = """<html>
    <style>
    #customers {
        font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%;
    }
    
    #customers td, #customers th {
        border: 1px solid #ddd;
        padding: 8px;
    }
    
    #customers tr:nth-child(even){background-color: #f2f2f2;}
    
    #customers tr:hover {background-color: #ddd;}
    
    #customers th {
        padding-top: 12px;
        padding-bottom: 12px;
        text-align: left;
        background-color: #4CAF50;
        color: white;
    }
    </style>
     
    <body>
     <!DOCTYPE html>
    <html>
    <body>
    """
    return body
def html_build_table(body,headers,entires):
    body = body + '''  <table>      <table id="customers">
        <tr>'''
    for header in headers:
        body = body+"<th>{}</th>\n".format(header)
    body = body + "</tr>\n"
    body = body + "<tr>\n"
    for entry in entires:
        for line in entry:
            body = body + '<td>{}</td>\n'.format(line)
        body = body + "</tr>\n"
    body = body+'</table>'
    
    return body


#print ('Running Config: ')
#pprint (pull_raw_data_data(hostname))
#print ('\n\n\nCDP DATA: ')
#pprint (pull_cdp_data(hostname))
#print ('\n\n\nInventory Data:')
#pprint (pull_inventory_data(hostname))
#print ("IP Int Brief Data:")
#pprint (pull_int_brief_data(hostname))
#print ("\n\n\nOSPF Data:")
#pprint (pull_osfp_data(hostname))
#print ("\n\n\nVersion Data:")
#pprint (pull_show_ver_data(hostname))
#print ("\n\n\nSubnet Data:")
#pprint (pull_subnet_data(hostname))

cdp_headers = ["select local_host",
				'Remote Device',
                "platform",
                "capabilities",
                "localInterface",
                "interface",
                "version",]

inv_headers = ["local_host",
                "descr",
                "name",
                "pid",
                "sn"]

ip_int_brief_headers = ["local_host",
						"intf",
						"ipaddr",]
						
ospf_headers = ["local_host","address","interface","neighbor_id","state"]						

show_ver_headers = ["local_host","version","uptime","running_image","config_register"]

subnet_data_headers = ["local_host","nexthop_if","network","mask"]



cdp_data = pull_cdp_data(hostname)
inv_data = pull_inventory_data(hostname)
int_brief_data = pull_int_brief_data(hostname)
ospf_data = pull_osfp_data(hostname)
ver_data = pull_show_ver_data(hostname)
subnet_data = pull_subnet_data(hostname)
running_config = pull_raw_data_data(hostname)[0][0]



body = html_build_start_body()
body = body + "<h2>{} Data</h2>".format (hostname)
body = body + "<h2>CDP Data</h2>"
body = html_build_table(body,cdp_headers,cdp_data)
body = body + "<h2>Inventory Data</h2>"
body = html_build_table(body,inv_headers,inv_data)
body = body + "<h2>IP Interface Brief</h2>"
body = html_build_table(body,ip_int_brief_headers,int_brief_data)
body = body + "<h2>OSPF Neighborships</h2>"
body = html_build_table(body,ospf_headers,ospf_data)
body = body + "<h2>Show Version Data</h2>"
body = html_build_table(body,show_ver_headers,ver_data)
body = body + "<h2>Subnets Data</h2>"
body = html_build_table(body,subnet_data_headers,subnet_data)
body = body + "<h2>Running Config</h2>"
body = body +'<pre>'
body = body + running_config
body = body +'</pre>'







body = body + """</table></body>
</html>
"""
output_doc = 'output.html'

to_doc_w(output_doc,body)

