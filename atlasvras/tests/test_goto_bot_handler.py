import pytest
from unittest.mock import patch, MagicMock
from atlasvras.g0t0 import goto_bot

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



def test_handle_help_message():
    fake_say = MagicMock()
    event = {
        "text": "@G0T0 help",
        "user": "U123ABC",
        "channel": "C456XYZ"
    }

    goto_bot.handle_mention(event, say=fake_say)

    fake_say.assert_called_once()
    assert "GOTO Bot Help" in fake_say.call_args[0][0]