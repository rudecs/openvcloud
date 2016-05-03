# mar/18/2014 09:29:12 by RouterOS 6.10
# software id = WLVA-21HW
#
/ip route remove [/ip route find static=yes]
/ip route
add comment="added by setup" distance=1 gateway=$gw
