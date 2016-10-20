#!/bin/bash

DISKS=()
FILESYSTEM="ext4"

echo "[+] analyzing system configuration"

source /etc/lsb-release

if [ "$DISTRIB_RELEASE" != "14.04" ]; then
	echo "[-] ubuntu version seems not correct, still in recovery ?"
	return 1
fi

if [ "$UID" != "0" ]; then
	echo "[-] you must be root"
	return 1
fi

if [ ! -f /proc/sys/net/ipv4/conf/backplane1/tag ]; then
	echo "[-] no backplane1 found"
	return 1
fi

echo "[+] discovering proxy"
BACKPLANE=$(ip -4 -o addr show dev backplane1 | awk '{ print $4 }' | cut -d'/' -f 1)
PROXHOST=$(echo $BACKPLANE | sed -r 's/([0-9]+.[0-9]+).([0-9]+.[0-9]+)/\1.2.254/')
if nc -w1 -z $PROXHOST 8123; then
	echo "[+] proxy found: $PROXHOST"
	echo "Acquire::http::Proxy \"http://$PROXHOST:8123\";" > /etc/apt/apt.conf.d/proxy
	
	if ! grep -q SHUTTLE /root/.bashrc; then
		echo "" >> /root/.bashrc
		echo "SHUTTLE=$PROXHOST" >> /root/.bashrc
	fi
	
else
	echo "[-] no proxy found at $PROXHOST"
fi


echo "[+] updating apt-get mirror list"
sed -i 's/us.archive/nl.archive/g' /etc/apt/sources.list

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
	
	# /mnt/ovs-db-write -> leftover ssd (full ssd)
	# /mnt/ovs-read     -> first ssd disk used for root
	# /var/tmp          -> second ssd disk used for root
	#
	# if nvme is present:
	# /mnt/ovs-db-write -> first ssd used for root
	# /mnt/ovs-read     -> nvme (full)
	# /var/tmp          -> second ssd used for root
	
	if [[ "${DISKS[@]}" == *"nvme"* ]]; then
		echo "[+] setup contains nvme disks"
		NVME_ENABLED=1
		
		for disk in ${DISKS[@]}; do		
			if [ "${disk}" == "nvme0n1" ]; then
				DISK_DBWRITE=/dev/$disk
			
			elif [ "$DISK_READ" == "" ]; then
				DISK_READ=/dev/$disk
			else
				DISK_VARTMP=/dev/$disk
			fi
		done
	else
		# default setup
		for disk in ${DISKS[@]}; do		
			if [ ! -e /dev/${disk}2 ]; then
				DISK_DBWRITE=/dev/$disk
			fi
			
			if [ -e /dev/${disk}2 ]; then
				if [ "$DISK_READ" == "" ]; then
					DISK_READ=/dev/$disk
				else
					DISK_VARTMP=/dev/$disk
				fi
			fi
		done
	fi
	
	if [ "$DISK_DBWRITE" == "" ]; then
		echo "[-] /mnt/ovs-db-write: cannot find usable ssd"
		return 1
	fi
	
	if [ "$DISK_READ" == "" ]; then
		echo "[-] /mnt/ovs-read: cannot find usable ssd"
		return 1
	fi
	
	if [ "$DISK_VARTMP" == "" ]; then
		echo "[-] /var/tmp: cannot find usable ssd"
		return 1
	fi
	
	if [ $NVME_ENABLED == 1 ]; then
		DBWRITE="${DISK_DBWRITE}p1"
		READ="${DISK_READ}5"
		VARTMP="${DISK_VARTMP}5"
	else
		DBWRITE="${DISK_DBWRITE}1"
		READ="${DISK_READ}5"
		VARTMP="${DISK_VARTMP}5"
	fi
	
	DBWRITE_SIZE=100%
	READ_SIZE=100%
	VARTMP_SIZE=100%
	
elif [ ${#DISKS[@]} == 2 ]; then
	echo "[+] building partitions: 2 SSD"
	
	# /mnt/ovs-db-write -> full space left on first ssd
	# /mnt/ovs-read     -> half space left on second ssd
	# /var/tmp          -> remain space left on second ssd
	
	# We take the larger ssd as the one which will be cut in two
	if [ $(cat /sys/block/${DISKS[0]}/size) -lt $(cat /sys/block/${DISKS[1]}/size) ]; then
		DISK_DBWRITE=/dev/${DISKS[0]}
		DISK_READ=/dev/${DISKS[1]}
		DISK_VARTMP=/dev/${DISKS[1]}
	else
		DISK_DBWRITE=/dev/${DISKS[1]}
		DISK_READ=/dev/${DISKS[0]}
		DISK_VARTMP=/dev/${DISKS[0]}
	fi
	
	COUNT_DISK1=$(grep ${DISK_DBWRITE}. /proc/partitions | wc -l)
	COUNT_DISK1=$(grep ${DISK_DBWRITE}. /proc/partitions | wc -l)
	COUNT_DISK1=$(grep ${DISK_DBWRITE}. /proc/partitions | wc -l)
	
	DBWRITE=${DISK_DBWRITE}5
	READ=${DISK_READ}5
	VARTMP=${DISK_VARTMP}6
	
	DBWRITE_SIZE=100%
	READ_SIZE=50%
	VARTMP_SIZE=100%
else
	echo "[-] this count of SSD are not supported"
	exit
fi

echo "[+] /mnt/ovs-db-write: will be on $DISK_DBWRITE ($DBWRITE)"
echo "[+] /mnt/ovs-read    : will be on $DISK_READ ($READ)"
echo "[+] /var/tmp         : will be on $DISK_VARTMP ($VARTMP)"

#
# /mnt/ovs-db-write
#
if [ $NVME_ENABLED == 1 ]; then
	echo "[+] cleaning /dev/nvme0n1"
	dd if=/dev/zero of=/dev/nvme0n1 bs=16M count=1 2> /dev/null
fi

TOTAL=$(parted $DISK_DBWRITE print | grep Disk | head -1 | awk '{ print $3 }')

# disk empty
if [ "$TOTAL" == "" ]; then
	echo "[ ] /mnt/ovs-db-write: no partition table found, creating it"
	parted $DISK_DBWRITE mklabel gpt > /dev/null
	
	TOTAL=$(parted $DISK_DBWRITE print | grep Disk | head -1 | awk '{ print $3 }')
	END="1049kB"
	
	if [ "$END" == "End" ]; then
		# Empty disk
		END="1049kB"
	fi
else
	END=$(parted $DISK_DBWRITE print | tail -2 | head -1 | awk '{ print $3 }')
fi
	
if [ "$TOTAL" != "$END" ]; then
	echo "[+] /mnt/ovs-db-write: partition will start at $END"
	parted -a optimal $DISK_DBWRITE mkpart ovs-db-write $FILESYSTEM $END $DBWRITE_SIZE > /dev/null
	
	PART=$(parted $DISK_DBWRITE print | tail -2 | head -1 | awk '{ print $1 }')
	
	if [ $NVME_ENABLED == 1 ]; then
		PART="p${PART}"
	fi
	
	if [ "${DISK_DBWRITE}$PART" != "$DBWRITE" ]; then
		echo "[-] /mnt/ovs-db-write: seems not correct according to script"
		return 1
	fi
else
	echo "[+] /mnt/ovs-db-write: disk seems already ready"
fi

#
# /mnt/ovs-read
#
TOTAL=$(parted $DISK_READ print | grep Disk | head -1 | awk '{ print $3 }')

if [ "$TOTAL" == "" ]; then
	echo "[ ] /mnt/ovs-read: no partition table found, creating it"
	parted $DISK_READ mklabel gpt > /dev/null
	
	TOTAL=$(parted $DISK_READ print | grep Disk | head -1 | awk '{ print $3 }')
	END="1049kB"
else
	END=$(parted $DISK_READ print | tail -2 | head -1 | awk '{ print $3 }')
	
	if [ "$END" == "End" ]; then
		# Empty disk
		END="1049kB"
	fi
fi
	
if [ "$TOTAL" != "$END" ]; then
	echo "[+] /mnt/ovs-read: partition will start at $END"
	parted -a optimal $DISK_READ mkpart ovs-read $FILESYSTEM $END $READ_SIZE > /dev/null
	
	PART=$(parted $DISK_READ print | tail -2 | head -1 | awk '{ print $1 }')
	
	if [ "${DISK_READ}$PART" != "$READ" ]; then
		echo "[-] /mnt/ovs-read: seems not correct according to script"
		return 1
	fi
else
	echo "[+] /mnt/ovs-read: disk seems already ready"
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
		return 1
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

for disk in $DBWRITE $READ $VARTMP; do
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

sed -i '/ovs-db-write/d' /etc/fstab
sed -i '/ovs-read/d' /etc/fstab
sed -i '/var\/tmp/d' /etc/fstab

UUID=$(blkid -o value -s UUID $DBWRITE)
echo "[+] /mnt/ovs-db-write ($DBWRITE) is $UUID"
echo "UUID=$UUID /mnt/ovs-db-write $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

UUID=$(blkid -o value -s UUID $READ)
echo "[+] /mnt/ovs-read ($READ) is $UUID"
echo "UUID=$UUID /mnt/ovs-read $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

UUID=$(blkid -o value -s UUID $VARTMP)
echo "[+] /var/tmp ($VARTMP) is $UUID"
echo "UUID=$UUID /var/tmp $FILESYSTEM discard,nobarrier,noatime,data=writeback 0 0" >> /etc/fstab

mkdir -p /mnt/ovs-db-write /mnt/ovs-read

echo "[+] mounting all the stuff"
mount -a
swapon -a
touch /mnt/ovs-db-write/.dontreportusage
touch /mnt/ovs-read/.dontreportusage

echo '[+] fixing permissions'
chmod 777 /tmp /var/tmp
chmod ugo+rwx,o+t /var/tmp

TEST=$(grep '^PermitRootLogin yes' /etc/ssh/sshd_config)
if [ "$TEST" == "" ]; then
	echo "[+] fixing ssh config and root login"
	sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
	service ssh restart
	echo "root:rooter" | chpasswd
	
else
	echo "[+] ssh already configured"
fi

echo "[+] setting up backplane1"
apt-get install -y openvswitch-switch
ifup --allow=ovs backplane1

echo "[+] pre-installing openvstorage dependancies"
apt-get install -y ntp kvm libvirt0 python-libvirt virtinst rabbitmq-server python-memcache \
    memcached lsscsi libvirt0 python-dev python-pyinotify sudo libev4 \
    python-boto nfs-kernel-server ipython devscripts openssh-server \
    python-paramiko python-pysnmp4 python-pika python-six python-protobuf python-pyudev sshpass \
    python-django nginx python-djangorestframework gunicorn python-gevent python-markdown \
    python-amqp python-anyjson libbz2-1.0 libc6 libcurl3 liblttng-ust0 libprotobuf8 libpython2.7 \
    librdmacm1 libsnappy1 libssl1.0.0 libstdc++6 libtokyocabinet9 libxml2 zlib1g \
    libcomerr2 libcurl3 libgssapi-krb5-2 libkrb5-3 liblttng-ust0 libomniorb4-1 libomnithread3c2 \
    git ssh python-pip

echo "[+] fixing some permissions"
chown syslog:adm /var/log/syslog /var/log/auth.log /var/log/kern.log

echo "[+] ensure that hosts file is correct for ovs"
if [ $(awk '/^127.0.0.1/ { print $2 }' /etc/hosts) == "localhost" ]; then
	HOSTLINE="127.0.0.1   $(hostname) localhost"
	sed -i "s/^127.0.0.1.*/$HOSTLINE/" /etc/hosts
fi

if ! grep -q ^PS1 /root/.bashrc; then
	echo "[+] setting up console"
	
	echo "" >> /root/.bashrc
	echo "PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]# '" >> /root/.bashrc
	source /root/.bashrc
fi

echo "[+] machine ready"
