import brnet


def test_create_object() -> None:
    _ = brnet.Brnet(
        user="pi",
        group="adm",
        interface="eth0",
        bridge="br0",
        number_of_taps=4,
        first_tap=0,
        wait_for_address=60,
        debug=False,
        dry_run=True,
    )
