#!/usr/bin/env python3

"""
parse_workspaces_hyprland.py

Goes through all workspaces with windows using hyprctrl
And returns a JSON list of text for each workspace, usually a Nerd font icon
"""

# EDIT THIS FOR YOUR OWN ICONS
# To find process name, you can use
# ps aux | grep <process>
# Then truncate the process down to 15 charactes
# ex:
# /bin/plasma-systemmonitor => plasma-systemmo
icon_map = {
        "firefox": "",
        "kitty": "",
        "emacs": "",
        "dolphin": "",
        "plasma-systemmo": "",
        "no-icon": "",
        "default": ""
}

import re
import json
import subprocess

import socket
import os, os.path
import time
from collections import deque

HYPRLAND_INSTANCE_SIGNATURE = os.getenv('HYPRLAND_INSTANCE_SIGNATURE')
SOCKET_PATH = f"/tmp/hypr/{HYPRLAND_INSTANCE_SIGNATURE}/.socket2.sock"

def main():
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
            else:
                current_window_title = ""

            clients_str = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True).stdout
            clients_json = json.loads(clients_str)

            icons = {}
            for client in clients_json:
                workspace = int(client['workspace']['id'])
                processname = client['class']

                if processname in icon_map:
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
