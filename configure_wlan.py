import json
import getpass
import pathlib


def main():
    ssid = input("Specify the SSID to which the Pico should connect: ")
    password = getpass.getpass("Specify the password for this network: ")

    wlan_config_file = pathlib.Path("pico_config/wlan.json")
    if wlan_config_file.exists():
        with open(wlan_config_file, "r") as f:
            wlan_config = json.load(f)

        if ssid in wlan_config.keys():
            yn = input(f"SSID {ssid} already exists in config. Overwrite? [yN]")
            if yn == "y":
                print("Overwriting existing SSID password ")
                wlan_config[ssid] = password
            else:
                print("Configuration file is not overwritten")
                return
        else:
            wlan_config[ssid] = password
    else:
        wlan_config = {
            ssid: password
        }

    pico_config_folder = pathlib.Path("pico_config")
    if not pico_config_folder.exists():
        pico_config_folder.mkdir()

    with open(wlan_config_file, "w") as f:
        json.dump(wlan_config, f, indent=4)


if __name__ == "__main__":
    main()
