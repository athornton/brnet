import argparse
import json
import logging
import os
import shlex
import shutil
import subprocess
import time
from typing import Union


class Brnet:
    """The class that sets up and tears down bridged networks.  Note that
    none of the arguments have defaults; we rely on the CLI to provide
    defaults for command-line usage."""

    def __init__(
        self,
        user: str,
        group: str,
        interface: str,
        bridge: str,
        number_of_taps: int,
        first_tap: int,
        wait_for_address: int,
        debug: bool,
    ) -> None:
        self._user = user
        self._group = group
        self._interface = interface
        self._bridge = bridge
        self._num_taps = number_of_taps
        self._first_tap = first_tap
        self._wait = wait_for_address
        self._debug = debug

        self._interfaces: dict[str, dict[str, Union[str, int]]] = {}

        self._logger = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
        self._logger.setLevel("INFO")
        if self._debug:
            self._logger.setLevel("DEBUG")
            self._logger.debug("Debugging enabled for Brnet")
        self.commands: list[str] = []  # Exposed for testing
        self._preflight_check()

    def execute(self, action: str) -> None:
        """execute() is the only public method.  It can either start
        or stop the bridged network.
        """
        if action == "start":
            self._start()
        elif action == "stop":
            self._stop()
        else:
            raise RuntimeError("Action must be either 'start' or 'stop'")

    @property
    def _ip(self) -> str:
        if self._interface not in self._interfaces:
            return ""
        iface = self._interfaces[self._interface]
        return f"{iface['ip_addr']}/{iface['prefixlen']}"

    def _preflight_check(self) -> None:
        if not shutil.which("ip"):
            raise RuntimeError(
                "'ip' not found on path; is 'iproute2' installed?"
            )

    def _run(
        self, cmd: str, check: bool = False
    ) -> subprocess.CompletedProcess:
        args = shlex.split(cmd)
        self._logger.debug(f"Running command '{cmd}'")
        self.commands.append(cmd)
        proc = subprocess.run(args, capture_output=True, check=check)
        if proc.returncode != 0:
            self._logger.warning(
                f"Command '{cmd}' failed: rc {proc.returncode}\n"
                + f" -> stdout: {proc.stdout.decode()}\n"
                f" -> stderr: {proc.stderr.decode()}"
            )
        else:
            self._logger.debug(
                f"Command '{cmd}' succeeded\n"
                + f" -> stdout: {proc.stdout.decode()}\n"
                f" -> stderr: {proc.stderr.decode()}"
            )
        return proc

    def _create_bridge(self) -> None:
        for cmd in [
            f"ip link add {self._bridge} type bridge",
            (
                f"ip link set dev {self._bridge} up address "
                + f"{self._interfaces[self._interface]['mac']}"
            ),
        ]:
            self._run(cmd, check=True)

    def _create_taps(self) -> None:
        for i in range(self._first_tap, (self._first_tap + self._num_taps)):
            tapdev = f"tap{i}"
            for cmd in [
                f"ip tuntap add mode tap {tapdev}",
                f"ip link set dev {tapdev} master {self._bridge} up",
            ]:
                self._run(cmd, check=True)

    def _get_gwinfo(self, iface: dict[str, Union[str, int]]) -> str:
        if "gateway" not in iface:
            return ""
        addl = f"via {iface['gateway']}"
        if "metric" in iface:
            addl += f" metric {iface['metric']}"
        return addl

    def _bridge_phys_if(self) -> None:
        iface = self._interfaces[self._interface]
        for cmd in [
            f"ip addr del dev {self._interface} {self._ip}",
            f"ip link dev {self._bridge} address {iface['mac']}",
            f"ip link dev {self._interface} master {self._bridge}",
            f"ip addr replace dev {self._bridge} {self._ip}",
        ]:
            self._run(cmd, check=True)
        addl = self._get_gwinfo(iface)
        for cmd in [
            f"ip route add default metric dev {self._bridge} {addl}",
            f"ip route del default dev {self._interface} {addl}",
        ]:
            self._run(cmd)

    def _extract_netinfo(self, interface: str) -> None:
        cmd = f"ip --json addr show dev {interface}"
        netinfo_resp = self._run(cmd)
        if netinfo_resp.stdout:
            netinfo = json.loads(netinfo_resp.stdout.decode())
            if type(netinfo) != list or len(netinfo) != 1:
                raise RuntimeError(
                    f"Info for {interface} should be a one-item list"
                )
        else:
            raise RuntimeError(
                f"No response when querying {interface} for address"
            )

        if interface not in self._interfaces:
            self._interfaces[interface] = {}
        self._interfaces[interface]["mac"] = netinfo[0]["address"]
        addrs = [x for x in netinfo[0]["addr_info"] if x["family"] == "inet"]
        retries = 0
        while len(addrs) < 1:
            if retries < self._wait and interface == self._interface:
                # Only wait for IP address on physical interface
                self._logger.debug(
                    f"Waiting 1s ({retries}/{self._wait}) for "
                    f"IPv4 address on {interface}"
                )
                time.sleep(1.0)
                addrs = [
                    x for x in netinfo[0]["addr_info"] if x["family"] == "inet"
                ]
            else:
                raise RuntimeError(
                    "There should be at least one IPv4 address for "
                    + interface
                )
        addr = addrs[0]
        if len(addrs) > 1:
            self._logger.info(
                f"Multiple addresses found for {interface}; using {addr}"
            )
        self._interfaces[interface]["ip_addr"] = addr["local"]
        self._interfaces[interface]["prefixlen"] = addr["prefixlen"]
        response = self._run(f"ip --json route show default dev {interface}")
        default_route = {}
        default_route_txt = ""
        if response.stdout:
            try:
                default_route_txt = response.stdout.decode()
                if not default_route_txt:
                    self._logger.warning(
                        f"Could not get default route for {interface}"
                    )
                    return
                default_route = json.loads(default_route_txt)
                if not default_route or len(default_route) == 0:
                    self._logger.info(f"No default route for {interface}")
                    return
                gateway = default_route[0]["gateway"]
                metric = default_route[0].get("metric")
                self._interfaces[interface]["gateway"] = gateway
                if metric is not None:
                    self._interfaces[interface]["metric"] = metric
                if len(default_route) > 1:
                    self._logger.info(
                        f"Using first default route for {interface} "
                        + f"-> gateway {gateway}, metric {metric}"
                    )
            except json.decoder.JSONDecodeError:
                self._logger.warning(
                    f"Could not JSON-decode default route for {interface}: "
                    + response.stdout.decode()
                )
            return
        else:
            self._logger.warning(
                f"Could not get output for default route for {interface}"
            )
            return

    def _remove_taps(self) -> None:
        for i in range(self._first_tap, (self._first_tap + self._num_taps)):
            tapdev = f"tap{i}"
            for cmd in [
                f"ip link set dev {tapdev} down",
                f"ip tuntap del mode tap {tapdev}",
            ]:
                self._run(cmd, check=True)

    def _debridge_interface(self) -> None:
        for cmd in [
            f"ip addr del {self._ip} dev {self._bridge}",
            f"ip link set dev {self._interface} nomaster",
            f"ip addr replace {self._ip} dev {self._interface}",
        ]:
            self._run(cmd, check=True)
        br_iface = self._interfaces[self._bridge]
        if "gateway" in br_iface:
            addl = self._get_gwinfo(br_iface)
            for cmd in [
                f"ip route add default {self._interface} {addl}",
                f"ip route del default dev {self._bridge} {addl}",
            ]:
                self._run(cmd)

    def _delete_bridge(self) -> None:
        for cmd in [
            f"ip link dev {self._bridge} down",
            f"ip link del {self._bridge} type bridge",
        ]:
            self._run(cmd, check=True)

    def _start(self) -> None:
        self._extract_netinfo(self._interface)
        self._create_bridge()
        self._create_taps()
        self._bridge_phys_if()

    def _stop(self) -> None:
        self._extract_netinfo(self._bridge)
        self._remove_taps()
        self._debridge_interface()
        self._delete_bridge()


def _str_bool(inp: str) -> bool:
    inp = inp.upper()
    if not inp or inp == "0" or inp.startswith("F") or inp.startswith("N"):
        return False
    return True


def main() -> None:
    """
    Parse arguments and set up a Brnet object.
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

    br = Brnet(
        user=args.user,
        group=args.group,
        interface=args.interface,
        bridge=args.bridge,
        number_of_taps=args.number_of_taps,
        first_tap=args.first_tap,
        wait_for_address=args.wait_for_address,
        debug=args.debug,
    )
    br.execute(args.action)


if __name__ == "__main__":
    main()
