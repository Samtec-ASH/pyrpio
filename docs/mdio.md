# MDIO

## MDIO History

Management Data Input/Output, or MDIO, is a 2-wire serial bus that is used to manage PHYs or physical layer devices in media access controllers (MACs) in Gigabit Ethernet equipment. The management of these PHYs is based on the access and modification of their various registers.

MDIO was originally defined in Clause 22 of IEEE RFC802.3. In the original specification, a single MDIO interface is able to access up to 32 registers in 32 different PHY devices. These registers provide status and control information such as: link status, speed ability and selection, power down for low power consumption, duplex mode (full or half), auto-negotiation, fault signaling, and loopback.

To meet the needs the expanding needs of 10-Gigabit Ethernet devices, Clause 45 of the 802.3ae specification provided the following additions to MDIO:

Ability to access 65,536 registers in 32 different devices on 32 different ports
Additional OP-code and ST-code for Indirect Address register access for 10 Gigabit Ethernet
End-to-end fault signaling
Multiple loopback points
Low voltage electrical specification
Theory of Operation

The MDIO bus has two signals: Management Data Clock (MDC) and Managment Data Input/Ouput (MDIO).

MDIO has specific terminology to define the various devices on the bus. The device driving the MDIO bus is identified as the Station Management Entity (STA). The target devices that are being managed by the MDC are referred to as MDIO Manageable Devices (MMD).

The STA initiates all communication in MDIO and is responsible for driving the clock on MDC. MDC is specified to have a frequency of up to 2.5 MHz.

## Clause 22

Clause 22 defines the MDIO communication basic frame format (figure 13) which is composed of the following elements:

Basic MDIO Frame Format

Figure 13: Basic MDIO Frame Format

ST	2 bits	Start of Frame (01 for Clause 22)
OP	2 bits	OP Code
PHYADR	5 bits	PHY Address
REGADR	5 bits	Register Address
TA	2 bits	Turnaround time to change bus ownership from STA to MMD if required
DATA	16 bits	Data
Driven by STA during write
Driven by MMD during read
The frame format only allows a 5-bit number for both the PHY address and the register address, which limits the number of MMDs that the STA can interface. Additionally, Clause 22 MDIO only supports 5V tolerant devices and does not have a low voltage option.

## Clause 45

In order to address the deficiencies of Clause 22, Clause 45 was added to the 802.3 specification. Clause 45 added support for low voltage devices down to 1.2V and extended the frame format (figure 14) to provide access to many more devices and registers. Some of the elements of the extended frame are similar to the basic data frame:

 Extended MDIO Frame Format

Figure 14: Extended MDIO Frame Format

ST	2 bits	Start of Frame (00 for Clause 45)
OP	2 bits	OP Code
PHYADR	5 bits	PHY Address
DEVTYPE	5 bits	Device Type
TA	2 bits	Turnaround time to change bus ownership from STA to MMD if required
ADDR/DATA	16 bits	Address or Data
Driven by STA for address
Driven by STA during write
Driven by MMD during read
Driven by MMD during read-increment-address
The primary change in Clause 45 is how the registers are accessed. In Clauses 22, a single frame specified both the address and the data to read or write. Clause 45 changes this paradigm. First an address frame is sent to specify the MMD and register. A second frame is then sent to perform the read or write.

The benefits of adding this two cycle access are that Clause 45 is backwards compatible with Clause 22, allowing devices to interoperate with each other. Secondly, by creating a address frame, the register address space is increased from 5 bits to 16 bits, which allows an STA to access 65,536 different registers.

In order to accomplish this, several changes were made in the composition of the data frame. A new ST code (00) is defined to identify Clause 45 data frames. The OP codes were expanded to specify an address frame, a write frame, a read frame, or a read and post read increment address frame. Since the register address is no longer needed, this field is replaced with DEVTYPE to specify the targeted device type. The expanded device type allows the STA to access other devices in addition to PHYs.

Additional details about Clause 45 can be found on the IEEE 802.3 workgroup website.