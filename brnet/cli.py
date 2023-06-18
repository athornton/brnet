#!/usr/bin/env python3
import argparse
import os
from .bridger import Bridger

def _str_bool(inp: str) -> bool:
    inp=upper(inp)
    if not inp or inp == "0" or inp.startswith("F") or inp.startswith("N"):
        return False
    return True

def main() -> None:
    """
    Parse arguments and set up a Bridger object.
    """
    parser = argparse.ArgumentParser(description="Set up bridged networking")
    parser.add_argument(
        "-u",
        "--user",
        default=os.environ.get("BRNET_USER","pi"),
        help="network-owner username"
    )
    parser.add_argument(
        "-g",
        "--group",
        default=os.environ.get("BRNET_GROUP","adm"),
        help="network wheel-equivalent group owner"
    )
    parser.add_argument(
        "-i",
        "--interface",
        default=os.environ.get("BRNET_INTERFACE","eth0"),
        help="network interface to convert to bridge"
    )
    parser.add_argument(
        "-b",
        "--bridge",
        default=os.environ.get("BRNET_BRIDGE_DEVICE","br0"),
        help="bridge network device"
    )
    parser.add_argument(
        "-n",
        "--number-of-taps",
        type=int,
        default=int(os.environ.get("BRNET_NUM_TAPS","4")),
        help="number of tap devices"
    )
    parser.add_argument(
        "-f",
        "--first-tap",
        type=int,
        default=int(os.environ.get("BRNET_FIRST_TAP","0")),
        help="number of first tap device"
    )
    parser.add_argument(
        "-m",
        "--metric",
        type=int,
        default=int(os.environ.get("BRNET_ROUTE_METRIC","101")),
        help="default route metric"
    )
    parser.add_argument(
        "-d",
        "--debug",
        type=bool,
        default=_str_bool(os.environ.get("DEBUG"),"")
        help="enable debug
    parser.add_argument(
        "action",
        choices=["start","stop"]
        help="Action to take"
)
    args=parser.parse_args()

    bridger = Bridger(
        user=args.user,
        group=args.group,
        interface=args.interface,
        bridge=args.bridge,
        number_of_taps=args.number_of_taps,
        first_tap=args.first_tap,
        metric=args.metric,
    )
    bridger.execute(args.action)

if __name__ == "__main__":
    main()

    
    
