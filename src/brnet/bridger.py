import json
import logging
import shutil
import time
from typing import Any, Dict, Optional

from .external import run, run_and_decode, run_check


class Bridger:
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
        metric: int,
        debug: bool,
    ) -> None:
        self._user = user
        self._group = group
        self._interface = interface
        self._bridge = bridge
        self._num_taps = number_of_taps
        self._first_tap = first_tap
        self._wait = wait_for_address
        self._metric = metric
        self._debug = debug

        self._orig_metric: Optional[int] = None

        self._logger = logging.getLogger(__name__)
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
        self._logger.setLevel("INFO")
        self._logger.info("Bridger created")
        if self._debug:
            self._logger.setLevel("DEBUG")
            self._logger.debug("Debugging enabled for Bridger")

        self._preflight_check()

        self._netinfo: Dict[str, Any] = {}
        self._gateway: str = ""

    def execute(self, action: str) -> None:
        """execute() is the only public method; it can either start or stop
        the bridged network."""
        if action == "start":
            self._start()
        elif action == "stop":
            self._stop()
        else:
            raise RuntimeError("Action must be either 'start' or 'stop'")

    @property
    def _ip(self) -> str:
        if not self._netinfo:
            return ""
        return f"{self._netinfo['local']}/{self._netinfo['prefixlen']}"

    def _preflight_check(self) -> None:
        if not shutil.which("ip"):
            raise RuntimeError(
                "'ip' not found on path; is 'iproute2' installed?"
            )

    def _extract_netinfo(self, interface: str) -> None:
        cmd = ["ip", "--json", "addr", "show", "dev", interface]
        netinfo = run_and_decode(args=cmd, logger=self._logger)
        if type(netinfo) != list or len(netinfo) != 1:
            raise RuntimeError("Netinfo should be a one-item list")
        addrs = [x for x in netinfo[0]["addr_info"] if x["family"] == "inet"]
        retries = 0
        while len(addrs) < 1:
            if retries < self._wait:
                self._logger.debug(
                    f"Waiting 1s ({retries}/{self._wait}) for "
                    f"IPv4 address on {self._interface}"
                )
                time.sleep(1.0)
                addrs = [
                    x for x in netinfo[0]["addr_info"] if x["family"] == "inet"
                ]
            else:
                raise RuntimeError(
                    "There should be at least one IPv4 address for "
                    + self._interface
                )
        addr = addrs[0]
        if len(addrs) > 1:
            self._logger.info(
                f"Multiple addresses found for {self._interface}; "
                f"using {addr}"
            )
        self._netinfo = addr
        self._logger.debug(f"Netinfo: {self._netinfo}")
        response = run(
            args=[
                "ip",
                "--json",
                "route",
                "show",
                "default",
                "dev",
                self._interface,
            ],
            logger=self._logger,
        )
        default_route = json.loads(response.stdout.decode())
        if not default_route or len(default_route) == 0:
            self._logger.info(f"No default route for {self._interface}")
            return
        gateway = default_route[0]["gateway"]
        metric = default_route[0].get("metric")
        if len(default_route) > 1:
            self._logger.info(
                f"Using first default route for {self._interface} "
                + f"-> gateway {gateway}, metric {metric}"
            )
        self._gateway = gateway
        self._orig_metric = metric

    def _start(self) -> None:
        self._extract_netinfo(self._interface)
        self._create_bridge()
        self._create_taps()
        self._bridge_phys_if()

    def _create_bridge(self) -> None:
        cmd = ["ip", "link", "add", self._bridge, "type", "bridge"]
        run_check(args=cmd, logger=self._logger)

    def _create_taps(self) -> None:
        for i in range(self._first_tap, (self._first_tap + self._num_taps)):
            tapdev = f"tap{i}"
            cmd = ["ip", "tuntap", "add", "mode", "tap", tapdev]
            run_check(args=cmd, logger=self._logger)
            cmd = ["ip", "link", "set", "dev", tapdev, "master", self._bridge]
            run_check(args=cmd, logger=self._logger)

    def _bridge_phys_if(self) -> None:
        cmd = ["ip", "addr", "del", "dev", self._interface, self._ip]
        run_check(args=cmd, logger=self._logger)
        cmd = ["ip", "addr", "replace", "dev", self._bridge, self._ip]
        run_check(args=cmd, logger=self._logger)
        cmd = ["ip", "link", "set", "dev", self._bridge, "up"]
        if self._gateway:
            cmd = [
                "ip",
                "route",
                "add",
                "default",
                "metric",
                str(self._metric),
                "dev",
                self._bridge,
                "via",
                self._gateway,
            ]
            run(args=cmd, logger=self._logger)
            cmd = ["ip", "route", "del", "default", "dev", self._interface]
            run(args=cmd, logger=self._logger)

    def _stop(self) -> None:
        self._extract_netinfo(self._bridge)
        self._remove_taps()
        self._debridge_interface()
        self._delete_bridge()

    def _remove_taps(self) -> None:
        for i in range(self._first_tap, (self._first_tap + self._num_taps)):
            tapdev = f"tap{i}"
            cmd = ["ip", "link", "set", "dev", tapdev, "down"]
            run_check(args=cmd, logger=self._logger)
            cmd = ["ip", "tuntap", "del", "mode", "tap", tapdev]
            run_check(args=cmd, logger=self._logger)

    def _debridge_interface(self) -> None:
        cmd = ["ip", "addr", "del", self._ip, "dev", self._bridge]
        run_check(args=cmd, logger=self._logger)
        cmd = ["ip", "link", "set", "dev", self._interface, "nomaster"]
        run_check(args=cmd, logger=self._logger)
        cmd = ["ip", "addr", "replace", self._ip, "dev", self._interface]
        run_check(args=cmd, logger=self._logger)
        if self._gateway:
            cmd = ["ip", "route", "add", "default"]
            if self._orig_metric:
                cmd.extend(["metric", str(self._orig_metric)])
            cmd.extend(["dev", self._interface, "via", self._gateway])
            run(args=cmd, logger=self._logger)
            cmd = ["ip", "route", "del", "default", "dev", self._bridge]

    def _delete_bridge(self) -> None:
        cmd = ["ip", "link", "del", self._bridge, "type", "bridge"]
        run_check(args=cmd, logger=self._logger)
