import pytest
from unittest.mock import patch, MagicMock
from atlasvras.g0t0 import goto_bot
from atlasvras.g0t0.goto_bot import make_lightcurve_plot
import os
import pandas as pd

@patch("atlasvras.g0t0.goto_bot.fetch_lightcurve_data")
@patch("atlasvras.g0t0.goto_bot.make_lightcurve_plot")
@patch("atlasvras.g0t0.goto_bot.app.client.files_upload_v2")

def test_handle_mention_success(mock_upload, mock_plot, mock_fetch):
    mock_say = MagicMock()
    event = {
        "text": "@G0T0 target SNtest RA=123.4 Dec=-45.6 plot=true",
        "user": "U123ABC",
        "channel": "C456XYZ"
    }

    # Mock the data fetch. The function returns a tuple (df, data_url) which we mock here
    mock_fetch.return_value = (
        MagicMock(),  # df is unused in this test
        "https://fakeurl.com/data.json"
    )
    mock_plot.return_value = "/tmp/fakeplot.png"

    goto_bot.handle_mention(event, say=mock_say)

    # Check if say was called with "Fetching..." and not an error
    assert any("Fetching data" in call.args[0] for call in mock_say.call_args_list)

    # Check file upload happened
    mock_upload.assert_called()
    upload_args = mock_upload.call_args.kwargs
    assert upload_args["channel"] == "C456XYZ"
    assert upload_args["file"] == "/tmp/fakeplot.png"



@patch("atlasvras.g0t0.goto_bot.app.client.chat_postEphemeral")
def test_handle_help_message(mock_ephemeral):
    fake_say = MagicMock()
    event = {
        "text": "@G0T0 help",
        "user": "U123ABC",
        "channel": "C456XYZ"
    }

    goto_bot.handle_mention(event, say=fake_say)

    # Check that the ephemeral message was sent
    mock_ephemeral.assert_called_once()
    args = mock_ephemeral.call_args.kwargs
    assert args["channel"] == "C456XYZ"
    assert args["user"] == "U123ABC"
    assert "GOTO Bot Help" in args["text"]



def test_make_lightcurve_plot_creates_file(tmp_path):
    # Dummy lightcurve data
    data = {
        "mjd": [60000.0, 60001.0, 60002.0],
        "forced_uJy": [100.0, 120.0, 90.0],
        "forced_uJy_uncert": [5.0, 6.0, 4.0],
        "forced_uJy_sigma_limit": [30.0, 30.0, 30.0],
        "filter": ["L", "L", "R"]
    }
    df = pd.DataFrame(data)

    path = make_lightcurve_plot(df)
    assert os.path.exists(path)
    assert path.endswith(".png")
    assert os.path.getsize(path) > 0

    os.remove(path)