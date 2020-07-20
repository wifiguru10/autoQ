#!/usr/bin/python3

import sys, os
import meraki
from time import sleep

print('Bounce Port Script')
print('Argument List:', str(sys.argv))

if len(sys.argv) < 4:
    print("Error: Usage ./autoQ_bounce.py <SN> <port> <seconds>")
    exit()
else:
    sn = sys.argv[1]
    switchPort = sys.argv[2]
    bounce = int(sys.argv[3])

    db = meraki.DashboardAPI(api_key=None, base_url='https://api.meraki.com/api/v0/', print_console=False)
    db.switch_ports.updateDeviceSwitchPort(sn,switchPort, enabled= False)
    sleep(bounce)
    db.switch_ports.updateDeviceSwitchPort(sn,switchPort, enabled= True)
    
    print(f'Bounce Completed for port {switchPort} on switch {sn}')

