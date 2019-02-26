import os
import re
import socket
import sys
import netmiko
from getpass import getpass
from ciscoconfparse import CiscoConfParse
from pprint import pprint
import ipaddress
import time
#from common_functions import *
def get_time():
	return time.ctime()

def get_ip_from_hostname(hostname):
	return socket.gethostbyname(hostname)

def ip_in_subnet_list(ip, subnets_list):
    address = ipaddress.ip_address(ip)
    for subnet in subnets_list:
        if address in subnet:
            return True
    return False

def get_subnets_from_file(file):
    subnets = []
    raw_subnets = read_doc_list (file)
    for line in raw_subnets:
        line = line.strip()
        subnets.append(ipaddress.ip_network(line, strict=False))
    return (subnets)

def find_parent_with_child(parent,child,file):
    parse = CiscoConfParse(file)
    par = parse.find_objects(parent)
    parent_list = []
    for obj in par:
        if obj.re_search_children(child):
            parent_list.append(obj.text)
    return parent_list

def pull_file_names_with_text(text):
	file_list = []
	files = os.listdir()
	for file in files:
		if text in file:
			file_list.append(file)
	return (file_list)

def get_mac (input):
	return(re.findall(r'(?:[0-9a-fA-F].?){12}', input))

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))
	
def read_doc_list (file_name):
	doc = []
	for line in open(file_name, 'r').readlines():
		doc.append(line)
	return doc

def to_doc_w(file_name, varable):
	f=open(file_name, 'w')
	f.write(varable)
	f.close()	

def to_doc_a(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.close()	

def is_it_a_phone(text):
	if len(re.findall(r'^SEP[0-9a-fA-F]{12}',text)) > 0:
		return True
	return False
	
def make_list_string_with_spaces(list):
	line = str(list)
	line = line.replace("[","")
	line = line.replace("]","")
	line = line.replace(","," ")
	line = line.replace("'"," ")
	return line


def make_connection(ip, username, password):
	try:
		net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)
		output = net_connect.send_command_expect("show ver")
		if "Nexus" in output:
			net_connect.disconnect()
			return netmiko.ConnectHandler(device_type='cisco_nxos', ip=ip, username=username, password=password)
		
		if "Cisco" not in output:
			if 'cisco' not in output:
				net_connect.disconnect()
				issue = ip + ", Not Cisco"
				to_doc_a("Issues.csv", issue)
				to_doc_a("Issues.csv", '\n')
				return None
		return net_connect
	except:
		try:
			return netmiko.ConnectHandler(device_type='cisco_ios_telnet', ip=ip, username=username, password=password)
		except:
			issue = ip + ", can't be ssh/telneted to"
			to_doc_a("Issues.csv", issue)
			to_doc_a("Issues.csv", '\n')
			return None


def find_child_text (file, text):
	all = []
	parse = CiscoConfParse(file)
	for obj in parse.find_objects(text):
		each_obj = []
		each_obj.append(obj.text)
		for each in obj.all_children:
			each_obj.append(each.text)
		all.append(each_obj)
	return all

def remove_end(line,remove_this):
	try:
		line_search = re.search(remove_this,line)
		line = line[:line_search.start()]
		return line
	except:
		return line
		
def remove_start(line,remove_this):
	try:
		line_search = re.search(remove_this,line)
		line = line[line_search.end():]
		return line
	except:
		return line

def merge_dics(dic1,dic2):
	z = {**dic1, **dic2}
	return z
	
def nslookup(input):
	nslookup = socket.getfqdn(str(input))	
	return nslookup

def run_command_on_net_connect(net_connect,command):
	return net_connect.send_command_expect(command)

def get_hostname (ssh_connect):
	return ssh_connect.find_prompt()[:-1]

def send_command(net_connect,command):
	return net_connect.send_command_expect(command)
