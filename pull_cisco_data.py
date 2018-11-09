from common_functions import *
import textfsm


def pull_show_ip_ospf_neighbor(net_connect):
	#Non diffrent commands for Nexus vs IOS, have to figure out if it's Nexus or IOS
	command = "show ip ospf neighbor"
	if 'CiscoNxosSSH' in str(type(net_connect)):
		command = "show ip ospf neighbor vrf all"
	output = net_connect.send_command(command , use_textfsm=True)
	#Output is also diffrent, just make it so the output has "interface", 'address','neighbor_id', and 'state' in it
	if "vrf" in command:
		for neighbor in output:
			if neighbor == ' ':
				return []
			neighbor['address'] = neighbor['local_ipaddr']
			neighbor['neighbor_id'] = neighbor['neighbor_ipaddr']
	if 'Invalid' in output:
		return []
	return output

def pull_invintory(net_connect):
	output = net_connect.send_command("show inventory", use_textfsm=True)
	if 'Invalid' in output:
		return []
	return output

def cdpNeighbors(txt):

    fields = [ ('deviceId', r'Device ID:\s*([\w\._-]+)'),
               ('ipAddress', r'IP(?:v4)? Address: (\d+\.\d+\.\d+\.\d+)'),
               ('platform', r'Platform: (\w[^,\r\n]*\w|\w)'),
               ('capabilities', r'Capabilities: (\w[^,\r\n]*\w|\w)'),
               ('localInterface', r'Interface: (\w[^,\r\n]*\w|\w)'),
               ('interface', r'Port ID \(outgoing port\): (\w[^,\r\n]*\w|\w)'),
               ('version', r'Version\s*:\s*\r?\n(\w[^\r\n]*)'),
               ('vtpDomain', r"VTP Management Domain(?: Name)?: '?(\w+)'?"),
               ('nativeVlan', r'Native VLAN: (\d+)'),
               ('duplex', r'Duplex: (\w[^\r\n]*\w|\w)')]
    for rawNeighbor in (n.group(1) for n in re.finditer(r'-{10,100}((?:.(?!-{10})){10,1500})', txt, re.S)):
        parsedNeighbor = dict()
        for label, exp in fields:
            m = re.search(exp, rawNeighbor, re.I)
            if m:
                parsedNeighbor[label] = m.group(1)
        if parsedNeighbor:
            yield parsedNeighbor

def pull_cdp(net_connect):
	final_output = []
	output = net_connect.send_command("show cdp neighbors detail")
	output = cdpNeighbors(output)
	for each in output:
		if "cca-" not in each['deviceId']:
			final_output.append(each)
		#Just made this change, Hopefully this removes the domain after the hostname from the remote devices name	
		each['deviceId'] = each['deviceId'].split('.')[0]
	return final_output



def pull_connected_routes(net_connect):
	connected_routes = []
	if 'CiscoNxosSSH' in str(type(net_connect)):
		output =  net_connect.send_command("show ip route", use_textfsm=True)
		if type(output) == str:
			return []
		for each in output:
			if each['protocol'] == 'local':
				connected_routes.append(each)
		if 'Invalid' in output:
			return []
		return connected_routes


	output = net_connect.send_command("show ip route", use_textfsm=True)
	#If the command doesn't sort it right skip this
	if type(output) == str:
		return []
	for each in output:
		if each['protocol']=='C':
			connected_routes.append(each)
	if 'Invalid' in output:
		return []
	return connected_routes

def pull_bgp(net_connect):
	output = net_connect.send_command("show ip bgp summary", use_textfsm=True)
	if 'Invalid' in output:
		return []
	return (output)


def pull_ip_int_brief(net_connect):
	return_this = []

	if 'CiscoNxosSSH' in str(type(net_connect)):
		output =  net_connect.send_command("show ip route", use_textfsm=True)
		for each in output:
			if len(each)<3:
				return []
			tmp_di= {}
			if each['protocol'] == 'local':
				tmp_di['intf'] = each['nexthop_if']
				tmp_di['ipaddr'] = each['nexthop_ip']
				return_this.append(tmp_di)
		if 'Invalid' in output:
			return []
		return return_this

	output = net_connect.send_command("sh ip interface brief", use_textfsm=True)
	if "ERROR" in output:
		return[]
	for each in output:
	
		if each['ipaddr'] != 'unassigned':
			return_this.append(each)
	return return_this


def pull_show_ver(net_connect):
	#Non diffrent commands for Nexus vs IOS, have to figure out if it's Nexus or IOS
	command = "show version"
	output = net_connect.send_command(command , use_textfsm=True)
	#Output is also diffrent, just make it so the output has "interface", 'address','neighbor_id', and 'state' in it
	try:
		output['RUNNING_IMAGE'] = output['BOOT_IMAGE']
		output['VERSION'] = output['OS']
		if 'CONFIG_REGISTER' not in output:
			output['CONFIG_REGISTER'] = "Unknown"
	except:
		pass
	if 'Invalid' in output:
		return []
	return output