# Azure Pico Demo

This repository contains the source code for a little demo that I describe in some detail on my blog under
[From Pi Pico to Azure with Micropython and Bicep](https://hiseyesuncovered.wordpress.com/2024/02/09/from-pi-pico-to-azure-with-micropython-and-bicep/).

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
mip.install("umqtt.simple")
```

### Setup the Azure IoT Hub

Of course, you could create you IoT hub manually through the Azure portal website. However for this
experiment, I wanted to implement a slightly more automatable approach by using 
[Bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview?tabs=bicep) and 
the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli). So, for the next
steps, make sure that you have the `az` tool installed and that you are logged into the Azure
subscription you want to use for the experiments.

I have chosen a few names and also my preferred location of the subscription and the IoT hub in the
file `azure/config.ps1`. If you prefer a different location and different subscription- and IoT-Hub
names, just change them in this file before continuing with the next steps.

Form a powershell on your local PC, run the following command:

```powershell
.\bringup.ps1
```

This will create a new resource group and within that, a new IoT hub. You can check this using the
Azure portal website.

### Prepare the Pico for IoT Hub connection

In order for the Raspberry Pi Pico to be allowed to send messages to the IoT-Hub, it needs to be
registered there. This happens by registering a new device in the IoT-Hub. For this I also created
a script. To create a new device that you want to call `pico1` (choose your own name here), you
simply run the following command on an powershell

```powershell
.\create_device.ps1 pico1
```

This will create a new device in the Azure IoT Hub and place a corresponding credentials file in
the `pico_config/` folder. In the above case you should find the file `pico_config/azure-pico1.json`.
This file needs to be copied to the Raspberry Pi, which can be done using `mpremote`. Note that we
copy the file **without the deviceid** and it will only be named `azure.json` on the device:

```
mpremote cp pico_config/azure-pico1.json :config/azure.json
```

Now everything is ready for the communication between the IoT hub and the device.

## Running everything

To start the Azure client on the Pico, you have to connect to the Pico using
`mpremote` and then run the following lines on the remote REPL:

```python
import demo
demo.main()
```

### What's implemented

All the functionality for IoT-Hub messages and direct methods is implemented in
`pico_src/demo.py`.

At the moment, the Pico could send a "Device2Cloud" message when a button is
pressed, in case you connected a button to GPIO14.

Additionally, you can send the plain text messages `led_on` and `led_off` as
"Cloud2Device" messages and the onboard LED of the Pico will be turned on or
off.

As an addition to the original article, I also implemented direct method
handling. On the Pico side you can now simply add new methods to the class
`DirectMethodHandler` to implement new methods. As a demo, I implemented a
method called `hello`. In order to call this method from the Azure portal,
you go to the "Direct Method" tab of your device and fill out the fields as
follows:

 - **Method name**: `hello`
 - **Payload**: 
```json
{
    "param1": "value1",
    "param2": 324
}
```

This will print `Called 'hello' with value1 and 324`. In the Azure portal,
you will also see a JSON document in the Result field which should look
somewhat like this:

```json
{
    "status": 200,
    "payload": {
        "result": "That is very good"
    }
}
```

When implementing your own direct methods this way, make sure that the JSON
field names match the names of the Python functions.
