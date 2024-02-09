import json
import network


def get_wlan():
    with open("config/wlan.json") as wlan_config_file:
        wlan_config = json.load(wlan_config_file)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    ssids = map(lambda entry: entry[0].decode(),
                wlan.scan())

    for ssid in ssids:
        if ssid in wlan_config.keys():
            wlan.connect(ssid, wlan_config[ssid]["password"])
            break
    else:
        print("No configured networks found")

    return wlan
