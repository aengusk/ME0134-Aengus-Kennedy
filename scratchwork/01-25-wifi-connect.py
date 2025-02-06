########################
# to list networks
########################

import network
import time
import ubinascii

station = network.WLAN(network.STA_IF)
station.active(True)

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)

print("Scanning...")
for _ in range(2):
    scan_result = station.scan()
    for ap in scan_result:
        print("SSID:%s BSSID:%s Channel:%d Strength:%d RSSI:%d Auth:%d "%(ap))
    print()
    time.sleep_ms(1000)


########################
# to connect
########################

import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('Tufts_Wireless', '')

while wlan.ifconfig()[0] == '0.0.0.0':
    print('.', end=' ')
    time.sleep(1)

# We should have a valid IP now via DHCP
print(wlan.ifconfig())

########################
# to test
########################

import urequests

url = 'https://v2.jokeapi.dev/joke/Any'
r = urequests.get(url)

if r.status_code == 200:
    print(r.text)
else:
	print('error: %s'%r.status_code)