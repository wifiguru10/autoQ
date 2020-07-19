# autoQ
Script to automatically quarantine or default a port based on the port TAG. 


# Steps

1. Tag the switch with "D:100" "Q:999" where D represents default data vlan for that witch and Q represents the quarantine segment
2. Run the script in the background (make sure to run 'export MERAKI_DASHBOARD_API_KEY="123123123"' in the shell before you run script)
3. Tag the desired port with "quarantine" to have the script automatically isolate that port. It'll re-tag the port with an upper "QUARANTINE" to show the action took place
4. Tag the quarantined port with "default" to have the port revert back to default (no isolation, default vlan)


# Demo of this script:
https://acecloud.webex.com/acecloud/ldr.php?RCID=27e77a8fd8f34b688a1457e30d2ab90a
Password: 2tP3PCVx

