#!/usr/bin/env python3

"""
parse_workspaces_hyprland.py

Goes through all workspaces with windows using hyprctrl
And returns a JSON list of text for each workspace, usually a Nerd font icon
"""

import re
import json
import subprocess

import socket
import os, os.path
import time
from collections import deque

# EDIT THIS FILE FOR YOUR OWN ICONS
# To find process name, you can use
# ps aux | grep <process>
# Then truncate the process down to 15 charactes
# ex:
# /bin/plasma-systemmonitor => plasma-systemmo
# 
# This will also match on the first word of window titles
icon_map_path = "/home/juge/.config/eww/scripts/workspaces_map.json"

HYPRLAND_INSTANCE_SIGNATURE = os.getenv('HYPRLAND_INSTANCE_SIGNATURE')
SOCKET_PATH = f"/tmp/hypr/{HYPRLAND_INSTANCE_SIGNATURE}/.socket2.sock"

def main():
    with open(icon_map_path, "r") as icon_map_buf:
        icon_map = json.loads(icon_map_buf.read())
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as socket_client:
        socket_client.connect(SOCKET_PATH)

        while True:
            # For now, do nothing about the actual content, and simply use it to refresh
            monitor_str = subprocess.run(["hyprctl", "monitors", "-j"], capture_output=True)
            monitor_json = json.loads(monitor_str.stdout)
            current_workspace = int(monitor_json[0]['activeWorkspace']['id'])

            activewindow_str = subprocess.run(["hyprctl", "activewindow", "-j"], capture_output=True)
            activewindow_json = json.loads(activewindow_str.stdout)
            if 'title' in activewindow_json:
                current_window_title = activewindow_json['title']
                if len(current_window_title) > 100:
                    current_window_title = current_window_title[:50] + "..." + current_window_title[-50:]
            else:
                current_window_title = ""

            clients_str = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True).stdout
            clients_json = json.loads(clients_str)

            icons = {}
            for client in clients_json:
                workspace = int(client['workspace']['id'])
                processname = client['class']
                win_title = client['title']

                if processname == "":
                    continue

                # First match on window title
                win_title = win_title.split(" ")[0]
                
                if win_title in icon_map:
                    icon = icon_map[win_title]
                elif processname in icon_map:
                    icon = icon_map[processname]
                else:
                    icon = icon_map['no-icon']

                if workspace in icons:
                    icons[workspace]["icons"].append(icon)
                else:
                    icons[workspace] = {
                        "icons": [icon],
                        "workspace": workspace,
                        "process": processname,
                        "current": True if current_workspace == workspace else False
                    }
            if current_workspace not in icons:
                icons[current_workspace] = {
                    "icons": [icon_map["default"]],
                    "workspace": current_workspace,
                    "processname": "<empty>",
                    "current": True
                }

            payload = {
                "title": current_window_title,
                "icons": [icons[i] for i in sorted(icons.keys())]
            }

            # This is a bit expensive, but there are only a few elements anyway
            print(json.dumps(payload), flush=True)

            # Block on next call
            line = socket_client.recv(1024).decode()

if __name__ == "__main__":
    main()
