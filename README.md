# eww-workspace-bar
Workspace overlay written for Eww

Works on X11 using wmctrl (view pre-Hyprland commits if you have issues)

Works on Hyprland using hyprctl (includes entire bar)

Shows an icon preview of workspaces like many bars, but is dynamic and based on the windows on particular workspaces.

Also supports multiple icons, 1 for each window.

![Preview with latte-dock](https://user-images.githubusercontent.com/23142073/224539013-6e5a7d8e-d9dc-4ebd-9564-d411e0278b42.png)

This bar only outputs as transparent, so this example is in conjunction with latte-dock on KDE Plasma 5.

## Tunables
You can/should edit a few things, namely in parse_workspaces.py, for your own custom icon map:

```py
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
```

There are also some tunables in the eww.yuck file itself:
```lisp
;; Enables process name preview on selected workspace
(defvar enable_process_name false)

;; Shows the workspace number beside the icon
(defvar enable_workspace_number true)

;; Enables multiple icon previews per workspace
(defvar enable_multiple_icons true)
```
