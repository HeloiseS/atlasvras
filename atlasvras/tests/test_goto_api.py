import pytest
import pandas as pd
from unittest.mock import patch
from atlasvras.g0t0.goto_bot import fetch_lightcurve_data, LightcurveTimeoutError

# Sample dummy response JSON
DUMMY_RESULTS = {
    "results": [
        {"mjd": 60000.1, "forced_mag": 18.5, "filter": "L"},
        {"mjd": 60001.2, "forced_mag": 18.7, "filter": "L"}
    ]
}

@patch("atlasvras.g0t0.goto_bot.requests.post")
@patch("atlasvras.g0t0.goto_bot.requests.get")
def test_fetch_success(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"dag_run_id": "FAKE_ID"}

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = DUMMY_RESULTS

    params = {
        "target_name": "SNTEST",
        "ra": 123.45,
        "dec": -45.6,
        "date_from": "2024-01-01",
        "date_to": "2024-06-01"
    }
    auth = ("user", "pass")
    df, url = fetch_lightcurve_data(params, auth)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "forced_mag" in df.columns
    assert "FAKE_ID" in url

@patch("atlasvras.g0t0.goto_bot.requests.post")
@patch("atlasvras.g0t0.goto_bot.requests.get")
def test_fetch_timeout(mock_get, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"dag_run_id": "TIMEOUT_ID"}

    mock_get.return_value.status_code = 404  # Never becomes available

    params = {
        "target_name": "SNDELAY",
        "ra": 111.1,
        "dec": -22.2,
        "date_from": "2024-01-01",
        "date_to": "2024-06-01"
    }
    auth = ("user", "pass")

    with pytest.raises(LightcurveTimeoutError) as excinfo:
        fetch_lightcurve_data(params, auth, timeout=3, poll_interval=1)

    assert "TIMEOUT_ID" in str(excinfo.value)