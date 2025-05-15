import pytest
from atlasvras.g0t0.parser import parse_target_command

@pytest.mark.parametrize("radec", [
    "RA=207.46183 Dec=+56.23112",
    "RA=207.46183 Dec=-56.23112",
])
def test_valid_decimal_coords(radec):
    text = f"@G0T0 target SN2025abc {radec} date_from=2024-01-01 plot=true"
    result = parse_target_command(text)
    assert result["target_name"] == "SN2025abc"
    assert result["ra"] == 207.46183
    assert abs(result["dec"]) == 56.23112
    assert result["plot"] is True

@pytest.mark.parametrize("radec", [
    "RA=13:49:50.84 Dec=56:13:52.0",         # colon-separated
    "RA=13h49m50.84s Dec=+56d13m52s",        # HMS/DMS
    "RA=13h49m50s Dec=+12:34:56",            # mixed
])
def test_invalid_coord_format(radec):
    text = f"@G0T0 target SN2025fail {radec} date_from=2025-01-01"
    with pytest.raises(ValueError, match="RA and Dec must be given in decimal degrees"):
        parse_target_command(text)

def test_invalid_number_format():
    text = "@G0T0 target SNbad RA=abc Dec=-12.3"
    with pytest.raises(ValueError, match="RA and Dec must be valid decimal numbers"):
        parse_target_command(text)