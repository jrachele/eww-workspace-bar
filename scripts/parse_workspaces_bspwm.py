#!/usr/bin/env python3

"""
parse_workspaces_bspwm.py

Goes through all workspaces with windows using bspc
And returns a JSON list of text for each workspace, on each monitor, usually a Nerd font icon
"""

import json
import subprocess

# EDIT THIS FILE FOR YOUR OWN ICONS
#
# To find the "key" for each of the icons
# Run xprop | grep WM_CLASS
# and click on the window of your choice
# Then choose the second option
#
# > xprop | grep WM_CLASS
# WM_CLASS(STRING) = "emacs", "Emacs"
#
# In this case my string would be "Emacs", not "emacs"

icon_map_path = "/home/juge/.config/eww/scripts/workspaces_map.json"
from pprint import pprint

def main():
    listen = subprocess.Popen(["bspc", "subscribe", "all"], stdout=subprocess.PIPE)
    while True:
        output = listen.stdout.readline() if listen.stdout is not None else None
        if listen.poll() is not None:
            break
        if output:
            parse_workspaces()


def parse_workspaces():
    with open(icon_map_path, "r") as icon_map_buf:
        icon_map = json.loads(icon_map_buf.read())

        monitors_str = subprocess.run(["bspc", "query", "-M", "--names"], capture_output=True)
        monitors = monitors_str.stdout.decode('UTF-8').strip().split('\n')

        clients = []
        window_title_str = subprocess.run(["xdotool", "getwindowfocus", "getwindowname"], capture_output=True)
        title = window_title_str.stdout.decode()

        for i, monitor_name in enumerate(monitors):
            monitor_json_str = subprocess.run(["bspc", "query", "-T", "-m", monitor_name], capture_output=True)
            monitor_json = json.loads(monitor_json_str.stdout.decode('UTF-8'))

            clients.append({})

            focused_desktop_id = monitor_json["focusedDesktopId"]
            current_workspace = None
            icons = {}
            for desktop in monitor_json["desktops"]:
                workspace = desktop['name']
                local_clients = []

                if desktop['id'] == focused_desktop_id:
                    current_workspace = workspace

                # Recursively get all clients on a desktop
                def recur_desktop(child):
                    if child is None: return
                    if 'client' in child and child['client'] is not None:
                        local_clients.append(child['client'])
                    if 'firstChild' in child and child['firstChild'] is not None:
                        recur_desktop(child['firstChild'])
                    if 'secondChild' in child and child['secondChild'] is not None:
                        recur_desktop(child['secondChild'])

                recur_desktop(desktop['root'])

                for client in local_clients:
                    processname = client['className']
                    urgent = client['urgent']

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
                            "current": True if current_workspace == workspace else False,
                            "urgent": False
                        }

                    icons[workspace]["urgent"] |= urgent


                if current_workspace is not None and current_workspace not in icons:
                    icons[current_workspace] = {
                        "icons": [icon_map["default"]],
                        "workspace": current_workspace,
                        "processname": "<empty>",
                        "current": True,
                        "urgent": False,
                    }


            clients[i] = {
                "name": monitor_name,
                "title": title.strip(),
                "icons": [icons[i] for i in sorted(icons.keys())],
            }

        print(json.dumps(clients), flush=True)

if __name__ == "__main__":
    main()
