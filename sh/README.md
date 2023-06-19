This is the original version of `brnet`, written in `bash`.  It has a
lot more requirements than the Python version.  Rather than `iproute2`
it assumes old-style `ifconfig` and requires `brctl` and `tunctl` as
well.

It's not recommended if your system is capable of running `iproute2`.

# Using with PiDP-11

You should run this script before you start the emulator.  When I did
that I found out simh was starting before my network interface had
acquired an address, so I wrote [wait_for_if](./wait_for_if) to pause
until the interface came up.  I then inserted the calls to `wait_for_if`
and `brnet` before the `rpcbind` call in `pidp11.sh`.

The diff to do that is [here](./pidp11.sh.diff).
