import logging
import shutil
from typing import Any, Dict

from .external import run_and_decode


class Bridger:
    def __init__(
        self,
        user: str,
        group: str,
        interface: str,
        bridge: str,
        number_of_taps: int,
        first_tap: int,
        metric: int,
        debug: bool,
    ) -> None:
        self._user = user
        self._group = group
        self._interface = interface
        self._num_taps = number_of_taps
        self._first_tap = first_tap
        self._metric = metric
        self._debug = debug

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

    def _preflight_check(self) -> None:
        for exe in ("ip", "tunctl"):
            if not shutil.which(exe):
                raise RuntimeError(f"{exe} not found on path")

    def execute(self, action: str) -> None:
        if action == "start":
            self._start()
        elif action == "stop":
            self._stop()
        else:
            raise RuntimeError("Action must be either 'start' or 'stop'")

    def _extract_netinfo(self, interface: str) -> Dict[str, Any]:
        cmd = ["ip", "--json", "show", "dev", interface]
        netinfo = run_and_decode(args=cmd, logger=self._logger)
        if type(netinfo) != list or len(netinfo) != 1:
            raise RuntimeError("Netinfo should be a one-item list")
        self._netinfo = netinfo[0]
