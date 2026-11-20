#!/usr/bin/env python3
"""On-screen ball viewer for PMW3360 motion received over USB serial."""
import argparse
import tkinter as tk
import threading
from queue import Queue, Empty

import serial 
from serial.tools import list_ports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", help="USB serial port (for example COM5 on Windows or /dev/ttyACM0 on Linux)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--sensitivity", type=float, default=1.0, help="Screen pixels per sensor count")
    args = parser.parse_args()
    updates = Queue()

    def receive():
        port = args.port
        if not port:
            ports = list(list_ports.comports())
            if len(ports) == 1:
                port = ports[0].device
            else:
                names = ", ".join(f"{item.device} ({item.description})" for item in ports) or "none found"
                updates.put(("status", f"USB serial ports: {names}. Restart with --port <port>."))
                return
        try:
            with serial.Serial(port, args.baud, timeout=1) as connection:
                updates.put(("status", f"Connected to {port}; move the sensor"))
                while True:
                    line = connection.readline().decode("ascii", errors="ignore").strip()
                    if line:
                        try:
                            dx, dy = map(float, line.split(",", 1))
                            updates.put(("motion", dx, dy))
                        except ValueError:
                            continue
        except (serial.SerialException, OSError) as error:
            updates.put(("status", f"USB serial error: {error}"))

    root = tk.Tk()
    root.title("PMW3360 Sensor Test")
    root.geometry("800x600")
    root.minsize(320, 240)
    root.configure(bg="#101820")
    status = tk.Label(root, text="Waiting for Raspberry Pi USB serial…", fg="white", bg="#101820", font=("Segoe UI", 12))
    status.pack(fill="x", padx=12, pady=10)
    canvas = tk.Canvas(root, bg="#172633", highlightthickness=0)
    canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    ball = canvas.create_oval(0, 0, 30, 30, fill="#47d7ac", outline="")
    position = [400.0, 300.0]

    def place_ball():
        width, height = canvas.winfo_width(), canvas.winfo_height()
        radius = 15
        position[0] = min(max(radius, position[0]), max(radius, width - radius))
        position[1] = min(max(radius, position[1]), max(radius, height - radius))
        canvas.coords(ball, position[0]-radius, position[1]-radius, position[0]+radius, position[1]+radius)

    def process():
        try:
            while True:
                update = updates.get_nowait()
                kind = update[0]
                if kind == "status":
                    status.config(text=update[1])
                else:
                    # Optical sensor Y is inverted relative to screen coordinates.
                    position[0] += update[1] * args.sensitivity
                    position[1] -= update[2] * args.sensitivity
                    place_ball()
        except Empty:
            pass
        root.after(16, process)

    threading.Thread(target=receive, daemon=True).start()
    canvas.bind("<Configure>", lambda _event: place_ball())
    process()
    root.mainloop()


if __name__ == "__main__":
    main()
