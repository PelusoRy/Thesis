from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
import re
from ipaddress import IPv4Network, IPv4Address 

nr = InitNornir(config_file="config.yaml")

#nr = nr.filter(F(hostname="172.16.2.1"))

def netmiko_send_commands_example(task):
    task.run(task=netmiko_send_command, command_string="show ip route ospf")


results = nr.run(task=netmiko_send_commands_example)
#print_result(results)

# Temp has the result of the command as a string
temp = results["R1"][1].__str__()

# ips has the networks host
ips = re.findall(r'O [\d./ ]+', temp)

# interfaces has the interfaces of the network
interfaces = re.findall(r'via [\d.]+', temp)

for x in range(0, len(ips)):
    temp = re.findall(r'[\d.]+/\d+', ips[x])
    temp2 = re.findall(r'[\d.]+', interfaces[x])
    ips[x] = [temp[0], temp2[0]]

print(ips)


print(IPv4Network(ips[0][0]).overlaps(IPv4Network(ips[1][0])))

if (IPv4Network(ips[0][0]).overlaps(IPv4Network(ips[1][0]))):
    print("Which network to fix?")
    for x in range(0, len(ips)):
        print(f"{x}: {ips[x][0]}")
    number = int(input("Number: "))
    network = IPv4Network(input("New Network (<network>/<mask>): ")) 

#print(network.netmask)

#print(str(network[1]))

#number = int(input("Number: "))

# Initialize nornir's object
router_to_configure = InitNornir(config_file="config.yaml")

# Filter the router that you want to configure
router_to_configure = router_to_configure.filter(F(hostname=ips[number][1]))

# Task that retrives the interfaces information
def netmiko_send_interface(task):
    task.run(task=netmiko_send_command, command_string="show ip interface brief")


results = router_to_configure.run(task=netmiko_send_interface)
#print_result(results)

router_info = results[list(results.keys())[0]][1].__str__()

# router_info has the required interfaces info
interface_info = re.findall(r'GigabitEthernet[\d] +[\d.]+', router_info)

print(interface_info)

for x in range(0, len(interface_info)):
    temp = re.findall(r'[\d]+.[\d.]+', interface_info[x])
    print(temp)
    addres = IPv4Address(temp[0])
    print(addres)
    if addres in IPv4Network(ips[number][0]):
        interface = re.findall(r'GigabitEthernet[\d]', interface_info[x])[0]

print(interface)

commands=[f"interface {interface}", 
          f"ip address {str(network[1])} {network.netmask}"]

print(commands)

router_to_configure = InitNornir(config_file="config.yaml")
router_to_configure = router_to_configure.filter(F(hostname=ips[number][1]))

results_config = router_to_configure.run(task=netmiko_send_config, config_commands=commands)

print_result(results_config)

commands=[f"interface {interface}", 
          f"ip dhcp pool {list(results_config.keys())[0]}",
          f"network {str(network[0])} {str(network.netmask)}",
          f"default-router {str(network[1])}"]

results_config = router_to_configure.run(task=netmiko_send_config, config_commands=commands)

print_result(results_config)

old_network = IPv4Network(ips[number][0])
commands=[f"router ospf 1",
          f"no network {str(old_network[0])} {str(old_network.hostmask)} area 0",
          f"network {str(network[0])} {str(network.hostmask)} area 0"]

results_config = router_to_configure.run(task=netmiko_send_config, config_commands=commands)

print_result(results_config)


