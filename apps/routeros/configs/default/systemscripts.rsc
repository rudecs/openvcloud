# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#

/system script
remove [/system script find name=reset_mac]
add name=reset_mac source="/interface ethernet reset-mac-address [/interface ethernet find]"
/system scheduler
remove [/system scheduler find name=reset_mac]
add name=reset_mac on-event=reset_mac start-time=startup interval=0


