# brnet

These is a networking tool to make running emulated systems under Linux
a little easier and more secure.

I have been using simh and klh10 a lot recently to emulate old computers
and operating systems.  Networking has been a particular pain because
most of these systems require raw access to the network devices, and
that typically means running the as root.

I didn't want to do that.  So I wrote brnet.

What this script does is to take the interface you specify (defaulting
to eth0) and turn it into a bridge device.  The using a user and group
you specify (it defaults to pi/adm, which is correct for a PiDP-11), it
creates a number of tap interfaces (defaulting to 4), and connects them
to the bridge too.

The point of doing that is so that you can run brnet with root
privileges to create network devices that another user can own and have
full control of without requiring escalated privileges.

After running brnet, you can therefore use, say, the `tap0` interface in
a guest system as your emulated ethernet device, and run as your normal
emulator user without sudo, and still have the network interface work.

# Using with PiDP-11

You should run this script before you start the emulator.  When I did
that I found out simh was starting before my network interface had
acquired an address, so I wrote [wait_for_if](./wait_for_if) to pause
until the interface came up.  I then inserted the calls to `wait_for_if`
and `brnet` before the `rpcbind` call in `pidp11.sh`.

The diff to do that is [here](./pidp11.sh.diff).

# Examples

To run using the defaults, which should work for a Raspberry Pi running
the PiDP-11 software: `brnet start`.

To run with a different user and group and more tap devices:

`brnet -u adam -g wheel -n 8 start`

To shut down the bridge and put things back the way they were:

`brnet stop`
