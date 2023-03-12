#!/usr/bin/env python3
"""
parse_workspaces.py

Goes through all workspaces with windows using wmctrl
And returns a JSON list of text for each workspace, usually a Nerd font icon
"""

import re
import json
import subprocess

# EDIT THIS FOR YOUR OWN ICONS
# To find process name, you can use
# ps aux | grep <process>
# Then truncate the process down to 15 charactes
# ex:
# /bin/plasma-systemmonitor => plasma-systemmo
icon_map = {
        "firefox": "",
        "kitty": "",
        "emacs-gtk": "",
        "dolphin": "",
        "plasma-systemmo": "",
        "no-icon": "",
        "default": ""
}


# Implementation
windows_pattern = r" (\d+) (\d+)\s"
desktop_pattern = r"(\d+)\s+\*"


def main():
    result = subprocess.run(["wmctrl", "-d"], capture_output=True)
    desktops_raw = result.stdout
    current_workspace = int(re.search(desktop_pattern, str(desktops_raw)).group(1))

    result = subprocess.run(["wmctrl", "-l", '-p'], capture_output=True)
    windows_raw = result.stdout
    workspace_pids = re.findall(windows_pattern, str(windows_raw), re.MULTILINE)

    icons = {}
    for (workspace, pid) in workspace_pids:
        workspace = int(workspace)

        result = subprocess.run(["ps", "-p", f"{pid}", "-o", "comm="],
                                capture_output=True)
        processname = str(result.stdout.strip())[2:-1]

        if processname in icon_map:
            icon = icon_map[processname]
        else:
            icon = icon_map["no-icon"]

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

    # This is a bit expensive, but there are only a few elements anyway
    print(json.dumps([icons[i] for i in sorted(icons.keys())]).replace("\\", "\\\\"))


if __name__ == "__main__":
    main()
