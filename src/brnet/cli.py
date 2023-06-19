#!/usr/bin/env python3
import argparse
import os

from .bridger import Bridger


def _str_bool(inp: str) -> bool:
    inp = inp.upper()
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
        default=os.environ.get("BRNET_USER", "pi"),
        help="network-owner username [env: BRNET_USER, 'pi']",
    )
    parser.add_argument(
        "-g",
        "--group",
        default=os.environ.get("BRNET_GROUP", "adm"),
        help="network wheel-equivalent group owner [env: BRNET_GROUP, 'adm']",
    )
    parser.add_argument(
        "-i",
        "--interface",
        default=os.environ.get("BRNET_INTERFACE", "eth0"),
        help=(
            "network interface to convert to bridge [env: BRNET_INTERFACE"
            + ", 'eth0']"
        ),
    )
    parser.add_argument(
        "-b",
        "--bridge",
        default=os.environ.get("BRNET_BRIDGE_DEVICE", "br0"),
        help="bridge network device [env: BRNET_BRIDGE_DEVICE, 'br0']",
    )
    parser.add_argument(
        "-n",
        "--number-of-taps",
        type=int,
        default=int(os.environ.get("BRNET_NUM_TAPS", "4")),
        help="number of tap devices [env: BRNET_NUM_TAPS, 4]",
    )
    parser.add_argument(
        "-f",
        "--first-tap",
        type=int,
        default=int(os.environ.get("BRNET_FIRST_TAP", "0")),
        help="number of first tap device [env: BRNET_FIRST_TAP, 0]",
    )
    parser.add_argument(
        "-w",
        "--wait_for_address",
        type=int,
        default=int(os.environ.get("BRNET_WAIT_FOR_ADDR", "60")),
        help="time (s) to wait for IP address [env: BRNET_WAIT_FOR_ADDR, 60]",
    )
    parser.add_argument(
        "-m",
        "--metric",
        type=int,
        default=int(os.environ.get("BRNET_ROUTE_METRIC", "101")),
        help="default route metric [env: BRNET_ROUTE_METRIC, 101]",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=_str_bool(os.environ.get("DEBUG", "")),
        help="enable debugging [env: DEBUG, False]",
    )
    parser.add_argument(
        "action", choices=["start", "stop"], help="Action to take"
    )
    args = parser.parse_args()

    bridger = Bridger(
        user=args.user,
        group=args.group,
        interface=args.interface,
        bridge=args.bridge,
        number_of_taps=args.number_of_taps,
        first_tap=args.first_tap,
        metric=args.metric,
        debug=args.debug,
    )
    bridger.execute(args.action)


if __name__ == "__main__":
    main()
