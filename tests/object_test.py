import json
import os
from pathlib import Path

import brnet

# Get the support directory
support = Path(__file__).parent / "support"

# Add the "ip" mock at the beginning of $PATH
os.environ["PATH"] = str(support) + os.pathsep + os.environ["PATH"]

# Set up our expected command lists
with open(support / "start_expected.txt") as f:
    expected_start = json.load(f)
with open(support / "stop_expected.txt") as f:
    expected_stop = json.load(f)


def test_create_object() -> None:
    br = brnet.Brnet(
        user="pi",
        group="adm",
        interface="eth0",
        bridge="br0",
        number_of_taps=4,
        first_tap=0,
        wait_for_address=60,
        debug=False,
    )
    br.execute("start")
    assert br.commands == expected_start
    br.commands = []
    br.execute("stop")
    assert br.commands == expected_stop
