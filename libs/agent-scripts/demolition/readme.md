# Demolition scripts

## Goal
Systems and components sometimes fail, that's a given but a cloud system needs to be able to cope with failure.
The scripts here create havoc to assist in testing failure scenario's.

## Sledge hammers
The `sledges` folder contains some scripts to brutally and without thinking take out a component. The `nodehammer.py` script for example simply turns of a node, simulating node failure.

## Orcs
In more complex scenario's then simply creating havoc without thought, an orc can be used to at least perform some logic before using the sledge hammer. The `ovsorc.py` for example knows which disk is write cache on the ovs system and can then use the `disk hammer` to kill it.  The orcs can be found in the `crew` folder.
