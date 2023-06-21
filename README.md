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

# Installing

`pip install brnet`, or check out the repository and do a `pip install
-e .`  You probably want to do this in a virtualenv, and if you do that,
you probably want to install a wrapper script as `/usr/local/bin/brnet`
to activate the appropriate virtualenv and then run the `brnet` command
(virtualenv activation will put the new stuff at the head of your
`$PATH`).  One approach to this is [here](./wrapper.sh).

Then you want to drop the following into `/etc/network/interfaces.d` to
start the network after the physical interface comes up.  I called my
file [`01-phys-to-bridge`](./01-phys-to-bridge).

# Examples

To run using the defaults, which should work for a Raspberry Pi running
the PiDP-11 software: `brnet start`.

To run with a different user and group and more tap devices:

`brnet -u adam -g wheel -n 8 start`

To shut down the bridge and put things back the way they were:

`brnet stop`

`brnet -h` will give you a help message explaining all the parameters.
