#!/usr/bin/env python3
"""
parse_workspaces.py

Goes through all workspaces with windows using wmctrl
And returns a JSON list of text for each workspace, usually a Nerd font icon
"""

import re
import json
import subprocess
import argparse

icon_map = {
        "firefox": "",
        "kitty": "",
        "emacs-gtk": "",
        "dolphin": "",
        "plasma-systemmo": "",
        "no-icon": "",
        "default": ""
}

windows_pattern = r" (\d+) (\d+)\s"
desktop_pattern = r"(\d+)\s+\*"


def main():
    parser = argparse.ArgumentParser(
                        prog='Parse Workspaces',
                        description='Utils for parsing wmctrl workspaces')

    group = parser.add_mutually_exclusive_group()
    group.required = True
    group.add_argument('-c', '--current', action='store_true', help="Get current workspace index")
    group.add_argument('-i', '--icon', help="Get icon at workspace index")
    group.add_argument('-l', '--list', action='store_true', help="Get list of icons at workspace index")

    args = parser.parse_args()
    result = subprocess.run(["wmctrl", "-d"], capture_output=True)
    desktops_raw = result.stdout
    current_workspace = int(re.search(desktop_pattern, str(desktops_raw)).group(1))
    if args.current:
        print(current_workspace)
        return

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
            # Append the icon to the list
            # TODO make this optional
            icons[workspace]["icons"].append(icon)
        else:
            icons[workspace] = {
                "icons": [icon],
                "workspace": workspace,
                "current": True if current_workspace == workspace else False
            }

    if current_workspace not in icons:
        icons[current_workspace] = {
            "icons": [icon_map["default"]],
            "workspace": current_workspace,
            "current": True
        }

    if args.icon:
        selected_icon = int(args.icon)
        if selected_icon not in icons:
            print(json.dumps([icon_map["default"]]).replace("\\", "\\\\"))
        else:
            print(json.dumps(icons[selected_icon]["icons"]).replace("\\", "\\\\"))
        return

    print(json.dumps([icons[i] for i in sorted(icons.keys())]).replace("\\", "\\\\"))


if __name__ == "__main__":
    main()
