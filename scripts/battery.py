#!/usr/bin/env python3

import subprocess
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: battery.py [-c | -s]")
        exit(-1)

    option = sys.argv[1]

    battery_icons = [
        '',
        '',
        '',
        '',
        '',
    ]
    charge_icons = [
        '',
        '',
    ]

    result = subprocess.run(["cat", "/sys/class/power_supply/BAT0/capacity"], capture_output=True)
    capacity = int(result.stdout)

    if (option == '-c'):
        icon = battery_icons[4] if capacity == 100 else battery_icons[capacity // 20]
        print(f"{icon}    {capacity}%")
        exit(0)
    elif (option == '-s'):
        result = subprocess.run(["cat", "/sys/class/power_supply/BAT0/status"], capture_output=True)
        status = str(result.stdout)[2:-3]
        icon = charge_icons[0] if status == "Charging" else charge_icons[1]
        print(f"{icon}  {status} ")
        exit(0)

    print("Usage: battery.py [-c | -s]")
    exit(-1)


if __name__ == "__main__":
    main()
