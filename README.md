# Azure Pico Demo

This repository contains the source code for a little demo that I describe in some detail on my blog under (From Pi Pico to Azure with Micropython and Bicep)[hiseyesuncovered.wordpress.com/].

## Getting started

### Requirements

To get this demo working, you will need the following:

 - Raspberry Pi Pico W
 - WLAN network with internet connection of the Pi Pico to connect to
 - An Azure subscription

### Setup

Install a Micropython firmware on you RaspberryPi Pico. For my experiments I used the
MicroPython version 1.22.1 but any newer version should work as well.

On your PC, clone this repository, create a virtual environment and install the
requirements:

```
python -mvenv .venv
.venv/Scripts/activate
pip install -r requirements.txt
```

Alternatively you can also just install the required "mpremote"-tool using any means
you prefer.

Once you have `mpremote` installed, you can download all project related Python sources
to the Pico:

```
mpremote cp pico_src/az_client.py :
mpremote cp pico_src/networking.py :
mpremote cp pico_src/demo.py :
```

### WLAN configuration

First we need to connec the Raspberry Pi Pico to a WLAN network so we can install some
needed libraries and then later connect to the Azure IoT Hub.

This project implements a simple wrapper to better separte configuration and passwords
from source code. You can either use the Python script `configure_wlan.py` to create
a corresponding JSON file or you create your own JSON file, according to the following
pattern:

```json
{
    "<Your SSID>": {
        "password": "<password for your SSID>"
    }
}
```

You can even add multiple SSIDs so that your Pico can connect to whatever SSID is currently available.

Once you have this file, just copy it to the Pico into the subdirectory `config` using `mpremote`:

```
mpremote fs mkdir config
mpremote cp pico_config/wlan.json :config/
```

### Installing depdencies on the Pico

The Azure client functionality requires a couple of additional libraries on the Pico. Now, with the
network configuration for the Wifi in place, we can download those directly from the Pico.

First connect to the REPL of the Pico using the mpremote command: `mpremote repl` and then run the
following Python commands from the Pico:

```python
import networking
networking.get_wlan()

import mip
mip.install("base64")
mip.install("hmac")
mip.install("umqtt")
```

