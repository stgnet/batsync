# batsync
Synchronize battery level across multiple Victron Multiplus in ESS mode

## Purpose
Where two or more Victron Multiplus installations exist, and one is downstream of the other, this Nodered code can be used to force the ESS Grid Set to pull or push power from/to the upstream installation to keep the SoC balanced between systems.

## Configuration
This assumes one primary Multiplus installation which may be off-grid, and does not require ESS itself.  The larger battery capacity and potentially most solar would be connected to this primary installation.  ACOUT from this installation is then tied to one or more additional Multiplus installations connected to their ACIN.  This does not preclude additional loads on the secondary unit's ACOUT.  There is also no reason that the Multiplus installations have to be the same battery voltage (i.e. tie between a 48v system and a 12v system is possible through ACOUT-ACIN).  It is also possible to have a primary installation be split phase (120/240) and secondary installations may be a matching split phase or only operate on a single phase.  The secondary installations must have ESS assistant loaded, and must be kept in optimized or external ESS mode (keep charged mode can be used to force the secondary to 100% if needed).

## Network
All the Multiplus installations require a GX controller, and a relatively accurate battery SoC tracking (directly from battery, shuntmeter, or if necessary built into multiplus) and all must be IP addressable for MQTT connections to persist.  The secondary installations would likely function behind a NAT if necessary, but a flat IP network with wired ethernet connections rather than WiFi would be best.  Internet connectivity isn't required.

## Installation
Along with ESS assistant, the Nodered code must be installed on each secondary node (the primary node just needs GX with MQTT enabled).  It has a site-specific dependency in the form of an MQTT read from the primary node, and the path to the SoC value on that GX.  So both the primary MQTT connection IP address must be adjusted to fit the local installation, and the MQTT IN ode must have the topic adjusted to read the primary battery SoC value.  Some other read values may be need to be tweaked for specific installation as well, such as the Multiplus input current limit path.
