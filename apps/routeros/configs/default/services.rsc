# mar/18/2014 09:25:34 by RouterOS 6.10
# software id = WLVA-21HW
#


/ip service set port=9080 numbers=[/ip service find name=www]
/ip service disable numbers=[/ip service find name=telnet]
/ip service set port=9021 numbers=[/ip service find name=ftp]
/ip service set port=9022 numbers=[/ip service find name=ssh]
