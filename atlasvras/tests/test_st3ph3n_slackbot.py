import runpy
from unittest.mock import patch, MagicMock

import pandas as pd 
import pytest 
from atlasapiclient.exceptions import ATLASAPIClientError

SERVER_ERROR = ATLASAPIClientError("Oops, status code is 500: Internal Server Error")

@pytest.fixture
def mocked_bot():
    eyeball = MagicMock(atlas_id_list_int=[1001], response_data=[{}])
    fasttrack = MagicMock(atlas_id_list_int=[1001], response_data=[{}])
    galcand = MagicMock(atlas_id_list_int=[], response_data=[])
    todo = MagicMock(response_data=[{'timestamp':'2026-09-30'}])

    with patch('atlasapiclient.client.RequestATLASIDsFromWebServerList', 
               side_effect=[eyeball, fasttrack, galcand]) as mock_list, \
         patch('atlasapiclient.client.RequestVRAToDoList', return_value=todo), \
         patch('atlasvras.utils.misc.fetch_vra_dataframe') as mock_fetch, \
         patch('slack_sdk.WebClient') as mock_webclient, \
         patch('time.sleep'):
        # Claude added mock_list to the yield for issue #31 (2026-10-01)
        yield mock_fetch, mock_webclient.return_value, mock_list


def test_slackbot_posts_message_after_3_failed_fetches(mocked_bot):
    mock_fetch, mock_slack, _ = mocked_bot
    mock_fetch.side_effect = SERVER_ERROR

    with pytest.raises(SystemExit):
        runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')
   
    assert mock_fetch.call_count == 3
    mock_slack.chat_postMessage.assert_called_once()
    assert mock_slack.chat_postMessage.call_args.kwargs['channel'] in ('#vra', '#vra-dev') 



def test_slackbot_recovers_when_retry_succeeds(mocked_bot):
    mock_fetch, mock_slack, _ = mocked_bot
    good_df = pd.DataFrame({'transient_object_id': [1001],
                            'apiusername': ['vra'],
                            'rank': [9.0],
                            'rank_alt1': [None]})

    mock_fetch.side_effect = [SERVER_ERROR, SERVER_ERROR, good_df]

    runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')

    assert mock_fetch.call_count == 3
    mock_slack.chat_postMessage.assert_called_once()
    assert 'Ingest Complete' in mock_slack.chat_postMessage.call_args.kwargs['text']


# Claude wrote this for issue #31 (2026-10-01) - HFS approved
def test_slackbot_posts_message_after_3_failed_eyeball_requests(mocked_bot):
    mock_fetch, mock_slack, mock_list = mocked_bot
    mock_list.side_effect = SERVER_ERROR

    with pytest.raises(SystemExit):
        runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')

    assert mock_list.call_count == 3
    assert mock_fetch.call_count == 0
    mock_slack.chat_postMessage.assert_called_once()
    assert mock_slack.chat_postMessage.call_args.kwargs['channel'] in ('#vra', '#vra-dev')


# Claude wrote this for issue #31 (2026-10-01) - HFS approved
def test_slackbot_recovers_when_eyeball_retry_succeeds(mocked_bot):
    mock_fetch, mock_slack, mock_list = mocked_bot
    eyeball = MagicMock(atlas_id_list_int=[1001], response_data=[{}])
    fasttrack = MagicMock(atlas_id_list_int=[1001], response_data=[{}])
    galcand = MagicMock(atlas_id_list_int=[], response_data=[])
    mock_list.side_effect = [SERVER_ERROR, SERVER_ERROR, eyeball, fasttrack, galcand]
    mock_fetch.return_value = pd.DataFrame({'transient_object_id': [1001],
                                            'apiusername': ['vra'],
                                            'rank': [9.0],
                                            'rank_alt1': [None]})

    runpy.run_module('atlasvras.st3ph3n.slackbot', run_name='__main__')

    assert mock_list.call_count == 5
    mock_slack.chat_postMessage.assert_called_once()
    assert 'Ingest Complete' in mock_slack.chat_postMessage.call_args.kwargs['text']
