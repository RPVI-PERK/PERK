# PMW3360 motion test

The Raspberry Pi reads PMW3360 motion over SPI and sends `dx`/`dy` values over TCP through its USB Ethernet gadget connection to a desktop window. The window moves a ball so the test does not take over the computer's actual mouse cursor.

## Wiring

Use the pin labels on your sensor breakout and connect its **3.3 V logic** to the Pi. For the Pi's default SPI0 pins: MOSI GPIO10 (pin 19), MISO GPIO9 (pin 21), SCLK GPIO11 (pin 23), CE0 GPIO8 (pin 24), 3V3 (pin 1 or 17), and GND (pin 6). Connect sensor NCS/CS to CE0. If using CE1, use GPIO7 (pin 26) and pass `--device 1`. Do not connect a 5 V sensor output to the Pi.

## Desktop

Install Python 3 on the computer and start the viewer:

```powershell
python desktop_viewer.py
```

Find the computer's IPv4 address on the **USB Ethernet adapter** with `ipconfig`. Allow Python through the Windows firewall on the private network if prompted.

## Raspberry Pi

Enable SPI with `sudo raspi-config` → Interface Options → SPI, then reboot. Install the required packages:

```bash
sudo apt update
sudo apt install -y python3-spidev
```

Copy `pi_sender.py` to the Pi. Start the Pi sender, replacing the example address with the computer's USB Ethernet IPv4 address:

```bash
python3 pi_sender.py --host 192.168.1.20
```


If you have the matching PMW3360 SROM firmware binary for your sensor, copy it to the Pi and add `--srom /path/to/firmware.bin`. The sensor requires its matching SROM for normal motion reporting; the firmware is not included in this project. The script checks the product ID at startup and loads the supplied SROM. Adjust `--sensitivity` on the desktop if the ball moves too slowly or quickly.

## Protocol

The Pi connects to TCP port 8765 and sends one JSON object per line, such as `{"dx":12,"dy":-4}`. Both devices need reachable IPv4 addresses on the USB Ethernet link. Start the desktop viewer before the Pi sender.
