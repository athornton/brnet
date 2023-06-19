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


def test_missing_parameter() -> None:
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            first_tap=0,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            wait_for_address=60,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            metric=101,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            debug=False,
        )
    with pytest.raises(TypeError):
        _ = brnet.Bridger(
            user="pi",
            group="adm",
            interface="eth0",
            bridge="br0",
            number_of_taps=4,
            first_tap=0,
            wait_for_address=60,
            metric=101,
        )


def test_extraneous_parameter() -> None:
    with pytest.raises(TypeError):
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
            extra=True,
        )
