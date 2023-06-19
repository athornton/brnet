import pytest

import brnet


def test_create_object() -> None:
    try:
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    except RuntimeError:
        # We may not have "ip" in the path, so preflight check could fail
        pass
