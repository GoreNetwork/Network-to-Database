from build_the_temp_database import *
#from build_perm_db import *
from pprint import pprint
from common_functions import *
from pull_cisco_data import *
from db_work import *
import multiprocessing
from itertools import repeat
import datetime


#perm_db_name = "network_data_db"
threads = 1

def get_username_password():
	username = 'cisco'
	password = 'cisco'
	return (username, password)


def deal_with_cdp_data(cdp_data, hostname, table_dics):
    #No phones at all
    if "cca-" in cdp_data['deviceId']:
        return
    if "SEP" in cdp_data['deviceId']:
        return
    #Don't SSH to Access-points
    if "AIR" not in cdp_data['platform']:
        try:
            ips = [cdp_data['ipAddress']]
            put_ips_in_todo_db(table_dics, ips)
        except:
            pass
    cdp_data = merge_dics (cdp_data, pull_currnet_data(hostname))
    #Puts the data into the database (see db_work.py)
    put_cdp_data_in_db(cdp_data,table_dics)


def pull_currnet_data(hostname):
    now = time.time()
    now = str(now).split('.')[0]
    test = {}
    test['local_host'] = hostname
    test['dls'] = now
    test['dau'] = now
    return test

def deal_with_int_brief(ips_brief,table_dics,hostname):
    current_data = pull_currnet_data(hostname)
    for tmp_ip in ips_brief:
        tmp_ip =  merge_dics(current_data,tmp_ip)
        insert_into_done(tmp_ip['ipaddr'],table_dics['tmp_db'])
        #insert_into_ip_int_brief(tmp_ip,'ip_int_brief',perm_db_name)
        insert_into_ip_int_brief(tmp_ip,table_dics)


def deal_with_ospf_data(ospf_data,table_dics,hostname):
    current_data = pull_currnet_data(hostname)
    insert_into_ospf(table_dics,ospf_data,current_data )
    for ospf_entry in ospf_data:
        ips = [ospf_entry['neighbor_id']]
        put_ips_in_todo_db(table_dics, ips)
    

def deal_with_inv(inv, hostname, table_dics):
    current_data = pull_currnet_data(hostname)
    insert_into_inv(table_dics,inv,current_data )

def deal_with_subnets(subnets, hostname, table_dics):
    current_data = pull_currnet_data(hostname)
    insert_into_connected_subnets(table_dics,subnets,current_data)


def deal_with_bgp(bgp_neighbors, hostname, table_dics):
    current_data = pull_currnet_data(hostname)
    insert_into_bgp(table_dics,bgp_neighbors,current_data)
    for bgp_nei in bgp_neighbors:
        ips = [bgp_nei['bgp_neigh']]
        put_ips_in_todo_db(table_dics, ips)

def deal_with_raw_commands(raw_commands, hostname, table_dics):
    current_data = pull_currnet_data(hostname)
    insert_into_raw_data(table_dics,raw_commands,current_data)


def deal_with_show_ver(show_ver, hostname, table_dics):
    current_data = pull_currnet_data(hostname)
    insert_into_show_ver(table_dics,show_ver,current_data)

            


#This does most of the work, the program is designed that you can pass this data to multiple threads and the main limit is
#CPU power on the server.  Currently I am using SQLite which doesn't support multiple connections so I'll need to move to a 
#real SQL server at some point to make this work.
def pull_cisco_data(username,password,table_dics):
    ip = pull_ip(table_dics['tmp_db'])
    if ip == "Done":
        return ip
    print (ip)
    #SSH/telnet to device
    net_connect = make_connection(ip, username, password)
    if net_connect == None:
        print ("can't connect to ",ip)
        return
    hostname = get_hostname (net_connect)
    cdp_list = pull_cdp(net_connect)

    for cdp_data in cdp_list:
        #add neighbor IPs IPs to do database
        #fill the perminate DB with CDP data
        deal_with_cdp_data(cdp_data, hostname, table_dics)
    
    #Pull show ip int brief data and put that data into the perm DB, and done IPs table of the tmp db
    ips_brief = pull_ip_int_brief(net_connect)
    deal_with_int_brief(ips_brief,table_dics,hostname)

    #Pull OSPF data, put that data into the perm DB, and the IPs into the ips_to_do table of the tmp db
    ospf_data = pull_show_ip_ospf_neighbor(net_connect)
    if len(ospf_data)>0:
        deal_with_ospf_data(ospf_data,table_dics,hostname)

    #Pull inventory and put it in the inventory table of the perm db    
    inv = pull_invintory(net_connect)
    if len(inv) > 0:
        deal_with_inv(inv, hostname, table_dics)

    #Pull connected subnets and put them into the perm db
    subnets = pull_connected_routes(net_connect)
    if len(subnets)> 0:
        deal_with_subnets(subnets, hostname, table_dics)

    bgp_neighbors = pull_bgp(net_connect)
    if len(bgp_neighbors)> 0:
        if type(bgp_neighbors) == list:
            deal_with_bgp(bgp_neighbors, hostname, table_dics)

    raw_commands={}
    raw_commands['show_run'] = run_command_on_net_connect(net_connect,'show run')
    deal_with_raw_commands(raw_commands, hostname, table_dics)

    show_ver = pull_show_ver(net_connect)
    deal_with_show_ver(show_ver, hostname, table_dics)

    net_connect.disconnect()



#Passing around the DB names and tables got to be a huge pain in the ass, so I am just passing this around
#If you make a change to the DB layout in build temp database be sure name make changes here
table_dics = {
    'tmp_db':{
    "db_name": 'temp.db',
    'to_do_table': 'to_do_ips',
	'done_table': "done",
    'issues_table': 'issues',
    },
    'perm_db': {
    'db_name': 'Current_network_db.db',
    'bgp':'bgp',
    'ip_brief':'ip_int_brief',
    'connected_subnets':'connected_subnets',
    'inventory':'inventory',
    'ospf':'ospf',
    'raw_data':'raw_data',
    'cdp':'cdp',
    'show_ver':'show_ver',},
}

#build_to_do_database(table_dics)



username, password= get_username_password()


build_to_do_database(table_dics)
print ("build_to_do_db")
done = False

if __name__ == "__main__":
    while done == False:

        with multiprocessing.Pool(processes=threads) as pool:
            for x in range(0,threads):
                multiple_results = [pool.apply_async(pull_cisco_data,(username, password,table_dics))]
            test = [res.get(timeout=300) for res in multiple_results]
            if test[0]=="Done":
                done = True
                time.sleep(60)

        #with multiprocessing.Pool(processes=100) as pool:
        #    for x in range(0,3000):
        #        multiple_results = [pool.apply_async(pull_cisco_data,(username, password,table_dics))]
        #        test = [res.get(timeout=300) for res in multiple_results]
        #        print (test)
        #        if test[0] == "Done":
        #            print ("Done")
        #            done = True
        #            time.sleep(300)
        #        
                
                
