# Claude rewrote this file for the slackbot refactor (2026-10-02)
import runpy
from unittest.mock import patch, MagicMock

import pytest

EXAMPLE_RESPONSE = [
    {'rank': 164437179,
     'id': 1204320230114824200,
     'atlas_designation': None,
     'other_designation': None,
     'ra': 310.83424,
     'dec': -11.80672,
     'ra_avg': 310.83425500000004,
     'dec_avg': -11.806716666666665,
     'object_classification': None,
     'sherlockClassification': 'SN',
     'followup_flag_date': '2026-10-01T07:36:42Z',
     'observation_status': '',
     'current_trend': 'fading 00.37 (w-w)',
     'earliest_mjd': 61312.896303,
     'earliest_mag': 18.67,
     'earliest_filter': 'w',
     'latest_mjd': 61313.937938,
     'latest_mag': 19.039,
     'latest_filter': 'w',
     'catalogue': None,
     'catalogue_object_id': None,
     'separation': None,
     'vra': 9.38061,
     'rb_pix': 0.980399,
     'date_modified': '2026-10-01T21:52:30',
     'external_crossmatches': None,
     'discovery_target': '1204320230114824200_61312.896_05r61313o0598w_2150_target',
     'rms': 0.195,
     'detection_list_id': 4,
     'images_id': 50014452},
    {'rank': 164438065,
     'id': 1231233940065354700,
     'atlas_designation': None,
     'other_designation': None,
     'ra': 348.14143,
     'dec': -6.89855,
     'ra_avg': 348.141406,
     'dec_avg': -6.898650000000001,
     'object_classification': None,
     'sherlockClassification': 'SN',
     'followup_flag_date': '2026-10-01T07:36:42Z',
     'observation_status': '',
     'current_trend': 'fading 00.33 (w-w)',
     'earliest_mjd': 61313.000658,
     'earliest_mag': 19.177,
     'earliest_filter': 'w',
     'latest_mjd': 61314.046266,
     'latest_mag': 19.509,
     'latest_filter': 'w',
     'catalogue': None,
     'catalogue_object_id': None,
     'separation': None,
     'vra': 9.8025,
     'rb_pix': 0.999877,
     'date_modified': '2026-10-02T00:03:25',
     'external_crossmatches': None,
     'discovery_target': '1231233940065354700_61313.000_05r61313o1543w_534_target',
     'rms': 0.559,
     'detection_list_id': 4,
     'images_id': 50014612},
]

LOW_VRA_RECORD = {**EXAMPLE_RESPONSE[0], 'id': 1000000000000000000, 'vra': 1.5}


def run_bot(eyeball, fasttrack, galcand):
    responses = [MagicMock(response_data=data) for data in (eyeball, fasttrack, galcand)]
    with patch('atlasapiclient.client.RequestATLASIDsFromWebServerList',
               side_effect=responses) as mock_list, \
         patch('slack_sdk.WebClient') as mock_webclient:
        runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')
    return mock_webclient.return_value, mock_list


def posted_text(mock_slack):
    mock_slack.chat_postMessage.assert_called_once()
    return mock_slack.chat_postMessage.call_args.kwargs['text']


def test_all_lists_populated_posts_all_sections():
    mock_slack, _ = run_bot(EXAMPLE_RESPONSE, EXAMPLE_RESPONSE + [LOW_VRA_RECORD], EXAMPLE_RESPONSE)

    text = posted_text(mock_slack)
    assert 'Ingest Complete' in text
    assert ':bell: 2 objects' in text
    assert '(1 with low ranks)' in text
    assert ':boom:  2 objects' in text
    assert ':stars:  2 objects' in text
    assert mock_slack.chat_postMessage.call_args.kwargs['channel'] == '#vra'


def test_all_lists_empty_exits_cleanly_without_message():
    with pytest.raises(SystemExit) as exit_info:
        run_bot([], [], [])

    assert exit_info.value.code == 0


def test_all_lists_empty_does_not_post():
    with patch('atlasapiclient.client.RequestATLASIDsFromWebServerList',
               side_effect=[MagicMock(response_data=[]) for _ in range(3)]), \
         patch('slack_sdk.WebClient') as mock_webclient, \
         pytest.raises(SystemExit):
        runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')

    mock_webclient.return_value.chat_postMessage.assert_not_called()


def test_only_eyeball_populated_posts_only_eyeball_section():
    mock_slack, _ = run_bot(EXAMPLE_RESPONSE, [], [])

    text = posted_text(mock_slack)
    assert ':boom:  2 objects' in text
    assert ':bell:' not in text
    assert ':stars:' not in text


def test_fasttrack_all_low_ranks():
    mock_slack, _ = run_bot([], [LOW_VRA_RECORD], [])

    text = posted_text(mock_slack)
    assert ':bell: 0 objects' in text
    assert '(1 with low ranks)' in text
    assert ':boom:' not in text


def test_requests_eyeball_fasttrack_galcand_in_order():
    _, mock_list = run_bot(EXAMPLE_RESPONSE, EXAMPLE_RESPONSE, EXAMPLE_RESPONSE)

    list_names = [call.kwargs['list_name'] for call in mock_list.call_args_list]
    assert list_names == ['eyeball', 'fasttrack', 'galcand']
