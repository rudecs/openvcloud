#to set ip addr to access default router os, on linux do (br0 is interface, change if needed)
ip a add 10.199.3.254/22 dev br0

#on routeros need to do (resets mac addr to addr used underneath)
interface ethernet reset-mac-address 0

