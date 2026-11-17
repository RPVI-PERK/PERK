#!/usr/bin/env python3
"""On-screen ball viewer that accepts PMW3360 dx/dy JSON lines over TCP."""
import argparse
import json
import socket
import tkinter as tk
import threading
from queue import Queue, Empty


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0", help="Address to listen on (default: all interfaces)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--sensitivity", type=float, default=1.0, help="Screen pixels per sensor count")
    args = parser.parse_args()
    updates = Queue()

    def receive():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen(1)
        updates.put(("status", f"Waiting for Raspberry Pi on TCP port {args.port}…"))
        while True:
            conn, address = server.accept()
            updates.put(("status", f"Connected to Raspberry Pi at {address[0]}"))
            with conn, conn.makefile("r", encoding="utf-8") as stream:
                for line in stream:
                    try:
                        data = json.loads(line)
                        updates.put(("motion", float(data.get("dx", 0)), float(data.get("dy", 0))))
                    except (ValueError, TypeError):
                        continue
            updates.put(("status", "Disconnected; waiting for Raspberry Pi…"))

    root = tk.Tk()
    root.title("PMW3360 Sensor Test")
    root.geometry("800x600")
    root.minsize(320, 240)
    root.configure(bg="#101820")
    status = tk.Label(root, text=f"Listening on port {args.port}; start pi_sender.py", fg="white", bg="#101820", font=("Segoe UI", 12))
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
