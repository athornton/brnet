import json
import shutil

class Bridger:
    def __init__(self,
                 user:str,
                 group:str,
                 interface:str,
                 bridge:str,
                 number_of_taps:int,
                 first_tap:int,
                 metric:int,
                 debug:bool,
                 ) -> None:
        self.user=user
        self.group=group
        self.interface=interface
        self.num_taps=number_of_taps
        self.first_tap=first_tap
        self.metric=metric
        self.debug=debug

        self._preflight_check()


    def _preflight_check(self) -> None:
        for exe in ("ip", "tunctl"):
            if not shutil.which(exe):
                raise RuntimeError(f"{exe} not found on path")

    def execute(self, action: str) -> None:
        if action=="start":
            self._start()
        elif action=="stop":
            self._stop()
        else:
            raise RuntimeError("Action must be either 'start' or 'stop'")
