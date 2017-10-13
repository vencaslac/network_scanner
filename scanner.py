# Notes:
#
#     This is not the complete scanner I have working in a production environment
#     I've purposefully left out everything reffering to logging and the specufics
#     of interpreting what hosts are whant, but this can easily be achieved by
#     adopting some kind of network wide naming scheme for devices and then adding
#     more string parsing to these results, or even adding more columns by
#     further expanding the interogation
#
#     DISCLAIMER:
#     Do not use this code in a proffesional environment, this is intended as a
#     showcase of what i've been working on and should not be considered viable or
#     production safe. I am not responsible if you get fired for running this code
#     on your network.
#
#     The code is provided as is without any implied warranty or implication of
#     safety or reliability.


import time                                                                       #used for... keeping time
import subprocess                                                                 #used for the actual pinging and network interogations
import ipaddress                                                                  #used for cycling through subnets without having to write our own code

def get_node_data(node):                                                          #this function interogates node for information and logs it as values in
    node_data=[]                                                                  #a string in order to then compile a list of results for the whole subnet

    node_data.append(str(time.time()).split('.')[0])                              #we firstly timestamp the operation, but we store the timestamp as a string (just chopping off the decimals as we don't need it down to the last nanosecond)
    node_data.append(str(node))                                                   #we add the IP that we're pinging to the result list


    command = subprocess.Popen(["ping","-n","1","-w","100", str(node)], stdout=subprocess.PIPE) #we send out a ping with a 100 ms time to live and listen for a reply
    reply = command.communicate()[0].decode('utf-8')

    if 'TTL' in reply:                                                           #we check for 'TTL' because this string shows up in multiple language windows when ping replies occur so this avoids having to localise the script
        node_data.append('Online')                                               #we conclude that this node is online, so we log it in the result list
        command = subprocess.Popen(["wmic","/node:%s"%(str(node)),"ComputerSystem","Get","Name"], stdout=subprocess.PIPE) #since this node responded to ping, we start by assuming this is a windows machine and will reply to a wmic request
        reply = command.communicate()[0].decode('utf-8')
        node_data.append(reply.split('\n')[1].split(' ')[0])                    #some string parsing without re because i'm a noob in order to pull the actual computer name from the reply (i wrote this at home on a late night with no network
                                                                                 #devices other than my pc around so you'll need to write some code to deal with these (i used 'ping -a' to get host names from dns but dns can mess up sometimes))
        command = subprocess.Popen(["wmic","/node:%s"%(str(node)),"ComputerSystem","Get","UserName"], stdout=subprocess.PIPE) #same as before only now we're interogating for a connected user
        reply = command.communicate()[0].decode('utf-8')
        node_data.append(reply.split('\n')[1].split('\\')[1].split(' ')[0])      #again with the string parsing
    else:
        node_data.append('Offline')                                              #we conclude that this node is not online as the reply didn't have a 'TTL' in it
        node_data.append('N/A')                                                  #dead nodes have no hostname
        node_data.append('N/A')                                                  #dead nodes have no users logged on

    print(node_data)                                                             #just so you know it's not stuck

    return '%s|%s|%s|%s|%s'%(node_data[0],node_data[1],node_data[2],node_data[3],node_data[4]) #we return everything as a string to the higher function


def scan_network(subnet=[]):                                                     #scans a single subnet
    net_scan=[]
    try:
        net=ipaddress.ip_network(subnet[0])
        for node in net:
             net_scan.append('%s|%s|%s\n'%(get_node_data(node),subnet[0],subnet[1])) #appends subnet specific data for the node so that they can be logged together
    except:
        print('failed to scan network:%s'%(str(net)))
    if len(net_scan)>1:
        [print(item) for item in net_scan]                                       #also just so you know it's not stuck

subnets=(item.split('|') for item in open('subnets.txt','r').readlines())         #creates a list of subnets as pairs of '|' separated values listed line by line in
                                                                                  #the 'subnets.txt' file. I made mine with two columns only but your needs may vary
[scan_network(subnet) for subnet in subnets]                                      #scans every network in the list

# Additional notes on functionality:
#
# This code outputs text to the console but you should be able to easily modify this
# in order to log the data to csv files that you can either parse as a whole or save
# on a per network, per user or per node basis in order to establish histories.
#
# Normally you would encase the last for loop in a "while True:" statement and just
# let it run and log, although sometimes it will get stuck in this form due to buffer
# limits i'm not really certain how to describe. Personally, i wrote a companion
# script that monitors the windows task list and ensures that any ping or wmic query
# lasts no longer than a few seconds before being killed but other solutions may
# be possible here
