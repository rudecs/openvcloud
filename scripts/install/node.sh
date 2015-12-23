#!/bin/bash

DISKS=()
FILESYSTEM="ext4"

echo "[+] analyzing system configuration"

source /etc/lsb-release

if [ "$DISTRIB_RELEASE" != "14.04" ]; then
	echo "[-] ubuntu version seems not correct, still in recovery ?"
	exit 1
fi

if [ "$UID" != "0" ]; then
	echo "[-] you must be root"
	exit 1
fi

LASTTIME=$(stat /var/lib/apt/periodic/update-success-stamp | grep Modify | cut -b 9-)
LASTUNIX=$(date --date "$LASTTIME" +%s)
echo "[+] last apt-get update: $LASTTIME"

if [ $LASTUNIX -gt $(($(date +%s) - (3600 * 6))) ]; then
	echo "[+] skipping system update"
else
	echo "[+] updating system"
	apt-get update
fi

# This package cause some automation problem with efi
echo shim hold | dpkg --set-selections
echo grub-pc hold | dpkg --set-selections

DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

for i in /sys/block/{sd?,nvme*}; do
	rot=$(cat $i/queue/rotational)
	
	if [ "$rot" = "0" ]; then
		DISKS+=("${i##*/}")
	fi
done

# Building partitions map
echo "[+] disks found: ${#DISKS[@]} (${DISKS[@]})"

NVME_ENABLED=0

if [ ${#DISKS[@]} == 3 ]; then
	echo "[+] building partitions: 3 SSD"
	
	# /mnt/cache1 -> leftover ssd (full ssd)
	# /mnt/cache2 -> first ssd disk used for root
	# /var/tmp    -> second ssd disk used for root
	#
	# if nvme is present:
	# /mnt/cache1 -> first ssd used for root
	# /mnt/cache2 -> nvme (full)
	# /var/tmp    -> second ssd used for root
	
	if [[ "${DISKS[@]}" == *"nvme"* ]]; then
		echo "[+] setup contains nvme disks"
		NVME_ENABLED=1
		
		for disk in ${DISKS[@]}; do		
			if [ "${disk}" == "nvme0n1" ]; then
				DISK_CACHE2=/dev/$disk
			
			elif [ "$DISK_CACHE1" == "" ]; then
				DISK_CACHE1=/dev/$disk
			else
				DISK_VARTMP=/dev/$disk
			fi
		done
	else
		# default setup
		for disk in ${DISKS[@]}; do		
			if [ ! -e /dev/${disk}2 ]; then
				DISK_CACHE1=/dev/$disk
			fi
			
			if [ -e /dev/${disk}2 ]; then
				if [ "$DISK_CACHE2" == "" ]; then
					DISK_CACHE2=/dev/$disk
				else
					DISK_VARTMP=/dev/$disk
				fi
			fi
		done
	fi
	
	if [ "$DISK_CACHE1" == "" ]; then
		echo "[-] /mnt/cache1: cannot find usable ssd"
		exit 1
	fi
	
	if [ "$DISK_CACHE2" == "" ]; then
		echo "[-] /mnt/cache2: cannot find usable ssd"
		exit 1
	fi
	
	if [ "$DISK_VARTMP" == "" ]; then
		echo "[-] /var/tmp: cannot find usable ssd"
		exit 1
	fi
	
	if [ $NVME_ENABLED == 1 ]; then
		CACHE1="${DISK_CACHE1}5"
		CACHE2="${DISK_CACHE2}p1"
		VARTMP="${DISK_VARTMP}5"
	else
		CACHE1="${DISK_CACHE1}1"
		CACHE2="${DISK_CACHE2}5"
		VARTMP="${DISK_VARTMP}5"
	fi
	
	CACHE1_SIZE=100%
	CACHE2_SIZE=100%
	VARTMP_SIZE=100%
	
elif [ ${#DISKS[@]} == 2 ]; then
	echo "[+] building partitions: 2 SSD"
	
	# /mnt/cache1 -> full space left on first ssd
	# /mnt/cache2 -> half space left on second ssd
	# /var/tmp    -> remain space left on second ssd
	
	# We take the larger ssd as the one which will be cut in two
	if [ $(cat /sys/block/${DISKS[0]}/size) -lt $(cat /sys/block/${DISKS[1]}/size) ]; then
		DISK_CACHE1=/dev/${DISKS[0]}
		DISK_CACHE2=/dev/${DISKS[1]}
		DISK_VARTMP=/dev/${DISKS[1]}
	else
		DISK_CACHE1=/dev/${DISKS[1]}
		DISK_CACHE2=/dev/${DISKS[0]}
		DISK_VARTMP=/dev/${DISKS[0]}
	fi
	
	COUNT_DISK1=$(grep ${DISK_CACHE1}. /proc/partitions | wc -l)
	COUNT_DISK1=$(grep ${DISK_CACHE1}. /proc/partitions | wc -l)
	COUNT_DISK1=$(grep ${DISK_CACHE1}. /proc/partitions | wc -l)
	
	CACHE1=${DISK_CACHE1}5
	CACHE2=${DISK_CACHE2}5
	VARTMP=${DISK_VARTMP}6
	
	CACHE1_SIZE=100%
	CACHE2_SIZE=50%
	VARTMP_SIZE=100%
else
	echo "[-] this count of SSD are not supported"
	exit
fi

echo "[+] /mnt/cache1: will be on $DISK_CACHE1 ($CACHE1)"
echo "[+] /mnt/cache2: will be on $DISK_CACHE2 ($CACHE2)"
echo "[+] /var/tmp   : will be on $DISK_VARTMP ($VARTMP)"

#
# /mnt/cache1
#
TOTAL=$(parted $DISK_CACHE1 print | grep Disk | head -1 | awk '{ print $3 }')

# disk empty
if [ "$TOTAL" == "" ]; then
	echo "[ ] /mnt/cache1: no partition table found, creating it"
	parted $DISK_CACHE1 mklabel gpt > /dev/null
	
	TOTAL=$(parted $DISK_CACHE1 print | grep Disk | head -1 | awk '{ print $3 }')
	END="1049kB"
else
	END=$(parted $DISK_CACHE1 print | tail -2 | head -1 | awk '{ print $3 }')
fi
	
if [ "$TOTAL" != "$END" ]; then
	echo "[+] /mnt/cache1: partition will start at $END"
	parted -a optimal $DISK_CACHE1 mkpart cache1 $FILESYSTEM $END $CACHE1_SIZE > /dev/null
	
	PART=$(parted $DISK_CACHE1 print | tail -2 | head -1 | awk '{ print $1 }')
	
	if [ "${DISK_CACHE1}$PART" != "$CACHE1" ]; then
		echo "[-] /mnt/cache1: seems not correct according to script"
		exit 1
	fi
else
	echo "[+] /mnt/cache1: disk seems already ready"
fi

#
# /mnt/cache2
#
TOTAL=$(parted $DISK_CACHE2 print | grep Disk | head -1 | awk '{ print $3 }')

if [ "$TOTAL" == "" ]; then
	echo "[ ] /mnt/cache2: no partition table found, creating it"
	parted $DISK_CACHE2 mklabel gpt > /dev/null
	
	TOTAL=$(parted $DISK_CACHE2 print | grep Disk | head -1 | awk '{ print $3 }')
	END="1049kB"
else
	END=$(parted $DISK_CACHE2 print | tail -2 | head -1 | awk '{ print $3 }')
fi
	
if [ "$TOTAL" != "$END" ]; then
	echo "[+] /mnt/cache2: partition will start at $END"
	parted -a optimal $DISK_CACHE2 mkpart cache2 $FILESYSTEM $END $CACHE2_SIZE > /dev/null
	
	PART=$(parted $DISK_CACHE2 print | tail -2 | head -1 | awk '{ print $1 }')
	
	if [ $NVME_ENABLED == 1 ]; then
		PART="p${PART}"
	fi
	
	if [ "${DISK_CACHE2}$PART" != "$CACHE2" ]; then
		echo "[-] /mnt/cache2: seems not correct according to script"
		exit 1
	fi
else
	echo "[+] /mnt/cache2: disk seems already ready"
fi

#
# /var/tmp
#
TOTAL=$(parted $DISK_VARTMP print | grep Disk | head -1 | awk '{ print $3 }')

if [ "$TOTAL" == "" ]; then
	echo "[-] /var/tmp: error occured when trying to find disk info"
fi

END=$(parted $DISK_VARTMP print | tail -2 | head -1 | awk '{ print $3 }')
	
if [ "$TOTAL" != "$END" ]; then
	echo "[+] /var/tmp: partition will start at $END"
	parted -a optimal $DISK_VARTMP mkpart tmp $FILESYSTEM $END $VARTMP_SIZE > /dev/null
	
	PART=$(parted $DISK_VARTMP print | tail -2 | head -1 | awk '{ print $1 }')
	
	if [ "${DISK_VARTMP}$PART" != "$VARTMP" ]; then
		echo "[-] /var/tmp: seems not correct according to script"
		exit 1
	fi
else
	echo "[+] /var/tmp   : disk seems already ready"
fi

#
# Cleaning and initializing disks
#

# Checking dependancies
# echo "[+] checking dependancies"
# TEST=$(dpkg -l | grep xfsprogs)
# if [ $? == 1 ]; then
#	apt-get install -y xfsprogs
# fi

for disk in $CACHE1 $CACHE2 $VARTMP; do
	echo "[+] cleaning $disk"
	dd if=/dev/zero of=$disk bs=16M count=1 2> /dev/null
	
	echo "[+] creating $FILESYSTEM partition on $disk"
	mkfs.$FILESYSTEM -q $disk
done

#
# Mounting point
#

#
# swap
#
echo "[+] setting up swap"

# cleaning fstab
sed -i '/swap/d' /etc/fstab

SWAPS=($(lsblk -fl | grep swap | awk '{ print $1 }' | xargs))
for swap in "${SWAPS[@]}"; do
	echo "[+] setting up swap partition: $swap"
	
	UUID=$(blkid -o value -s UUID /dev/$swap)
	echo "UUID=$UUID none swap sw 0 0" >> /etc/fstab
done

#
# our partitions
#
echo "[+] setting up our new partitions"

sed -i '/cache1/d' /etc/fstab
sed -i '/cache2/d' /etc/fstab
sed -i '/var\/tmp/d' /etc/fstab

UUID=$(blkid -o value -s UUID $CACHE1)
echo "[+] /mnt/cache1 ($CACHE1) is $UUID"
echo "UUID=$UUID /mnt/cache1 $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

UUID=$(blkid -o value -s UUID $CACHE2)
echo "[+] /mnt/cache2 ($CACHE2) is $UUID"
echo "UUID=$UUID /mnt/cache2 $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

UUID=$(blkid -o value -s UUID $VARTMP)
echo "[+] /var/tmp ($VARTMP) is $UUID"
echo "UUID=$UUID /var/tmp $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

mkdir -p /mnt/cache1 /mnt/cache2

echo "[+] mounting all the stuff"
mount -a
swapon -a
touch /mnt/cache1/.dontreportusage
touch /mnt/cache2/.dontreportusage

echo '[+] fixing permissions'
chmod ugo+rwx,o+t /var/tmp

echo "[+] fixing ssh config and root login"
sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
service ssh restart
echo "root:rooter" | chpasswd

echo "[+] setting up backplane1"
apt-get install -y openvswitch-switch
ifup --allow=ovs backplane1

echo "[+] machine ready"
