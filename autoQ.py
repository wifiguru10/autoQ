#!/usr/bin/python3

import meraki
from datetime import datetime
import time
from time import sleep


#*****************************************************USER SETTINGS BELOW

adminEmail = "ndarrow@cisco.com" #this is the only admin that will trigger the script execution
TS  = 3 #interval in seconds
org_id = '121177' #your ORGID

tag_exclude = "NOAPI"   #Network Wide, Switch or Port level. Use this tag to exclude from being changed/read
tag_VVLAN = "V:"         #TAG on switch indicating voice vlan 'V:555' would represent vlan 555 
tag_QLAN = "Q:"         #same as above for quarantine
tag_DLAN = "D:"         #same as above for data

tag_action_isolate = 'quarantine'
tag_action_default = 'default'

qvlan_default = 999
dvlan_default = 101
vvlan_default = 102

WRITE = True    #Set to False to test the script (read-only)

#*****************************************************USER SETTINGS ABOVE

db = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v0/', print_console=False)


#returns device object {'name': 'Test Switch', 'tags': 'quarantine', 'model': 'MS220-8P', }
def get_SW(db,net_id, switchName):
    devs = db.devices.getNetworkDevices(net_id)
    for d in devs:
        if d['model'][:2] == "MS" and d['name'] == switchName:
            return d
    return

def get_VQD(tags):
    vqd = {}
    if tag_VVLAN in tags and tag_QLAN in tags and tag_DLAN in tags:
        tmp = tags.split(' ')
        for t in tmp:
            if t[:2] == tag_VVLAN and t[2:].isdigit():
                vqd['V'] = t[2:] 
            if t[:2] == tag_QLAN and t[2:].isdigit():
                vqd['Q'] = t[2:]
            if t[:2] == tag_DLAN and t[2:].isdigit():
                vqd['D'] = t[2:]
    return vqd


#Main Loop
while True:

    cl30 = db.change_log.getOrganizationConfigurationChanges(org_id,timespan=TS+2)
    for cl in cl30:
#       print(cl)
        if cl['adminEmail'] == adminEmail:
            newV = cl['newValue'] #what did it change to
            oldV = cl['oldValue'] #what was it before
            if "Tags" in newV: #was the change a tag
                print("Tag Change detected!")

                #THIS IS WHERE THE PORT WILL GET ISOLATED
                if tag_action_isolate in newV: #is the port quarantined?
                    if not tag_action_isolate in oldV: #is it a new quarantine? prevents other tag changes from triggering
                        print("\nPORT GETTING QUARANTINED")
                        print(cl)
                        switchName = cl['label'].split('/')[0].strip() #Gets name from  'Switch / 2' 
                        switchPort = cl['label'].split('/')[1].strip() #Gets port from  'Switch / 2'
                        net_id = cl['networkId']    
                        sw = get_SW(db,net_id,switchName) #returns switch object
                        sn = sw['serial']
                        vqd = get_VQD(sw['tags']) #{'D': '101', 'Q': '999', 'V': '202'} Parsed Voice/Data/Quarantine vlanID
                        print(f'Parsed VQD[{vqd}]')
                        print(f'Switch[{switchName}] Port[{switchPort}] Serial[{sn}]')
                        port = db.switch_ports.getDeviceSwitchPort(sn,switchPort) 
                        print(port)
                        if port['type'] == 'access' and not tag_exclude in port['tags']: #is it access port and not excluded?
                            newTag = port['tags'].replace(tag_action_isolate,'').strip() + " " + tag_action_isolate.upper()
                            print(newTag)
                            print("WRITING")
                            if 'Q' in vqd:
                                qvlan = int(vqd['Q'])
                            else:
                                qvlan = qvlan_default

                            if(WRITE): result = db.switch_ports.updateDeviceSwitchPort(sn,switchPort,vlan=qvlan,tags=newTag, isolationEnabled=True, )
                            print(result)
                        elif not port['type'] == 'access':
                            print("Port is not an access port. Removing TAG")
                            newTag = port['tags'].replace(tag_action_isolate,'').strip()
                            if(WRITE): result = db.switch_ports.updateDeviceSwitchPort(sn,switchPort,tags=newTag)

                #THIS IS WHERE THE PORT WILL GET DEFAULTED
                if tag_action_default in newV: #is the port defaulted
                    if not tag_action_default in oldV:
                        print("\nPORT GETTING QUARANTINED")
                        print(cl)
                        switchName = cl['label'].split('/')[0].strip() #Gets name from  'Switch / 2' 
                        switchPort = cl['label'].split('/')[1].strip() #Gets port from  'Switch / 2'
                        net_id = cl['networkId']    
                        sw = get_SW(db,net_id,switchName) #returns switch object
                        sn = sw['serial']
                        vqd = get_VQD(sw['tags']) #{'D': '101', 'Q': '999', 'V': '202'} Parsed Voice/Data/Quarantine vlanID
                        print(f'Parsed VQD[{vqd}]')
                        print(f'Switch[{switchName}] Port[{switchPort}] Serial[{sn}]')
                        port = db.switch_ports.getDeviceSwitchPort(sn,switchPort) 
                        #print(port)
                        if port['type'] == 'access' and not tag_exclude in port['tags']: #is it access port and not excluded?
                            newTag = port['tags'].replace(tag_action_default,'').strip()
                            newTag = newTag.replace(tag_action_isolate.upper(),'').strip()
                            print("WRITING")
                            if 'D' in vqd:
                                dvlan = int(vqd['D'])
                            else:
                                dvlan = dvlan_default
                            if(WRITE): result = db.switch_ports.updateDeviceSwitchPort(sn,switchPort,vlan=dvlan,tags=newTag, isolationEnabled=False)
                            #print(result)
                        elif not port['type'] == 'access':
                            print("Port is not an access port. Removing TAG")
                            newTag = port['tags'].replace(tag_action_default,'').strip()
                            if(WRITE): result = db.switch_ports.updateDeviceSwitchPort(sn,switchPort,tags=newTag)

    print('.')
    sleep(TS)
