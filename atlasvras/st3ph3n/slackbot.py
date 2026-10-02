#!/usr/bin/env python
"""
ST3PH3N SLACK BOT
=================
This is the eyeball notification bot that alerts when an ingest has finished
and there are objects with rank > 4 in the eyeball and fast track lists.


2026-10-01: added retyr logic and error message sending to 
two steps that are likely to fall appart if server overloaded: 
- RequestATLASIDsFromWebServerList (because it asks for all the eyeball list in a time period)
- fetch_vra_dataframe (super large  period if loads of junk - WE KNOW THIS ONE FELL OVER)
"""
from atlasapiclient import client as atlasapiclient
from atlasapiclient.utils import API_CONFIG_FILE, MJD_EPOCH_DATE
from atlasapiclient.exceptions import ATLASAPIClientError
from atlasvras.utils.misc import fetch_vra_dataframe
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import pandas as pd
import yaml
import pkg_resources
from time import sleep



#########################################
# LOAD PATHS AND TOKENS FROM THE CONFIG FILE
#########################################

BOT_CONFIG_FILE = pkg_resources.resource_filename('atlasvras', 'data/bot_config_MINE.yaml')

with open(BOT_CONFIG_FILE, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        LOG_PATH = config['log_path']
        SLACK_TOKEN = config['slack_token_st3ph3n']
        URL_BASE = config['base_url']
        EYEBALL_THRESHOLD = config['eyeball_threshold']
        URL_SLACK = config['url_slack']
    except yaml.YAMLError as exc:
        print(exc)


# SUMMONING THE SLACK BOT
client = WebClient(token=SLACK_TOKEN)


get_hi_from_eyeball = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                    list_name='eyeball',
                                    get_response=True,
                                    datethreshold=MJD_EPOCH_DATE,
                                    vra_gte=7
                                    )

N_hi_eyeball = len(get_hi_from_eyeball.response_data)

# Get ATLAS IDS from the fast track eyeball list -> set fast track
get_all_from_fasttrack = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='fasttrack',
                                         get_response=True,
                                         datethreshold=MJD_EPOCH_DATE
                                         )

if len(get_all_from_fasttrack.response_data) == 0:
    N_fasttrack=0
else:
    fasttrack_df = pd.DataFrame(get_all_from_fasttrack.response_data)
    N_hi_fasttrack = fasttrack_df[fasttrack_df.vra>=EYEBALL_THRESHOLD].shape[0]
    N_lo_fasttrack = fasttrack_df[fasttrack_df.vra<EYEBALL_THRESHOLD].shape[0]
    N_fasttrack = fasttrack_df.shape[0]

# Counting the number of events in the Galactic candidate list
get_all_from_galcand = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='galcand',
                                         get_response=True,
                                         datethreshold=MJD_EPOCH_DATE
                                         )
N_gal_candidates = len(get_all_from_galcand.response_data)

# OUTPUTS
bot_message = f"*Ingest Complete*\n"

if N_hi_eyeball == 0 and N_fasttrack == 0 and N_gal_candidates==0:
    # If nothing in Fast track or eyeball or fasstrack end the script without sending a message
    # exit 0 = ALL GOOD, exit 1 means something went wrong. Changed now (2026-10-02)
    exit(0)

if N_fasttrack>0:
    bot_message += (f":bell: {N_hi_fasttrack} objects with rank > {EYEBALL_THRESHOLD}. "
                f"({N_lo_fasttrack} with low ranks): :link:"
                f"<{URL_BASE}followup_quickview/8/|Fast Track List>\n\n")

if N_hi_eyeball>0:
    bot_message += (f":boom:  {N_hi_eyeball} objects with rank > {EYEBALL_THRESHOLD}. :link: "
               f"<{URL_BASE}followup_quickview/4/?vra__gte={EYEBALL_THRESHOLD}&sort=-vra| Extragalactic Candidates>\n"
               )

if N_gal_candidates> 0:
    bot_message += (f":stars:  {N_gal_candidates} objects. "
                f":link:"
                f"<{URL_BASE}followup_quickview/12/| Galactic Candidates>\n\n")

# SENDING SLACK MESSAGE
try:
    response = client.chat_postMessage(
        channel="#vra",
        text=bot_message
    )
except SlackApiError as e:
    print(f"Error sending message: {e.response['error']}")
