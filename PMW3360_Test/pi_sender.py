#!/usr/bin/env python3
"""Read PMW3360 motion over SPI and send dx/dy JSON lines over TCP."""
import argparse
import json
import socket
import time

import spidev


class PMW3360:
    REG_PRODUCT_ID = 0x00
    REG_REVISION_ID = 0x01
    REG_POWER_UP_RESET = 0x3A
    REG_MOTION_BURST = 0x50
    REG_SROM_ENABLE = 0x13
    REG_SROM_LOAD_BURST = 0x62
    REG_SROM_ID = 0x2A
    REG_CONFIG2 = 0x10

    def __init__(self, bus, device, speed_hz=25_000, srom=None):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)  # CE0 is device 0; CE1 is device 1
        self.spi.max_speed_hz = speed_hz
        self.spi.mode = 3
        self.spi.bits_per_word = 8
        time.sleep(0.05)
        self.write(self.REG_POWER_UP_RESET, 0x5A)
        time.sleep(0.05)
        for reg in (0x02, 0x03, 0x04, 0x05, 0x06):
            self.read(reg)  # clear startup state as specified by the datasheet
        product = self.read(self.REG_PRODUCT_ID)
        revision = self.read(self.REG_REVISION_ID)
        if product != 0x42:
            raise RuntimeError(f"Unexpected PMW3360 product ID 0x{product:02x} (expected 0x42)")
        if srom:
            self.load_srom(srom)
        else:
            print("No SROM file supplied; motion may be unavailable until sensor firmware is loaded.")
        print(f"PMW3360 detected (revision 0x{revision:02x})")

    def write(self, reg, value):
        self.spi.xfer2([reg | 0x80, value])
        time.sleep(0.0002)

    def read(self, reg):
        # Keep NCS asserted across address and data. At 25 kHz, the address
        # byte itself provides the required read-address/data settling time.
        response = self.spi.xfer2([reg & 0x7F, 0])
        return response[1]

    def load_srom(self, filename):
        with open(filename, "rb") as firmware:
            data = firmware.read()
        if not data:
            raise ValueError("SROM file is empty")
        self.write(self.REG_CONFIG2, 0x00)  # disable Rest mode for the download
        self.write(self.REG_SROM_ENABLE, 0x1D)
        time.sleep(0.01)
        self.write(self.REG_SROM_ENABLE, 0x18)
        # Keep chip select asserted for the full SROM burst. The low SPI clock
        # provides more than the required inter-byte delay.
        self.spi.xfer2([self.REG_SROM_LOAD_BURST, *data])
        time.sleep(0.0002)
        srom_id = self.read(self.REG_SROM_ID)
        if srom_id == 0:
            raise RuntimeError("SROM download did not verify (SROM_ID is zero)")
        self.write(self.REG_CONFIG2, 0x00)  # wired mouse configuration
        print(f"Loaded {len(data)} SROM bytes (ID 0x{srom_id:02x})")

    @staticmethod
    def signed16(low, high):
        value = low | (high << 8)
        return value - 65536 if value & 0x8000 else value

    def motion(self):
        # A single transfer preserves NCS and the slow clock gives the sensor
        # its required burst address-to-data delay.
        data = self.spi.xfer2([self.REG_MOTION_BURST] + [0] * 12)[1:]
        motion, _observation, dx_l, dx_h, dy_l, dy_h = data[:6]
        return bool(motion & 0x80), self.signed16(dx_l, dx_h), self.signed16(dy_l, dy_h)

    def close(self):
        self.spi.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, help="Computer's USB Ethernet IPv4 address")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bus", type=int, default=0)
    parser.add_argument("--device", type=int, default=0, help="SPI chip select: 0=CE0, 1=CE1")
    parser.add_argument("--srom", help="PMW3360 SROM firmware binary, if available")
    parser.add_argument("--rate", type=float, default=100, help="Sample rate in Hz")
    args = parser.parse_args()

    sensor = PMW3360(args.bus, args.device, srom=args.srom)
    try:
        print(f"Connecting to viewer at {args.host}:{args.port} …")
        with socket.create_connection((args.host, args.port)) as connection:
            print("Connected. Move the sensor; press Ctrl+C to stop.")
            interval = 1.0 / max(1.0, args.rate)
            while True:
                started = time.monotonic()
                motion, dx, dy = sensor.motion()
                if motion:
                    payload = json.dumps({"dx": dx, "dy": dy}) + "\n"
                    connection.sendall(payload.encode("utf-8"))
                    print(f"dx={dx:5d} dy={dy:5d}", end="\r")
                time.sleep(max(0, interval - (time.monotonic() - started)))
    finally:
        sensor.close()


if __name__ == "__main__":
    main()
