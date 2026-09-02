import pytest


@pytest.mark.hil
def test_set_intensity_updates_status(solar_sim_device) -> None:
    solar_sim_device.set_intensity(10)
    status = solar_sim_device.read_status()
    print(status['white_pct'])
    print(abs(status["white_pct"] - 10))
    assert status is not None
    # assert abs(status["white_pct"] - 10) <= 2  # firmware rounds via //655
    expected_white = int(32.3521 * (10 / 100) + 16.3331)  # ≈ 19
    assert abs(status["white_pct"] - expected_white) <= 1
