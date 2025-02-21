#!/usr/bin/env python
"""
ST3PH3N SLACK BOT
=================
This is the eyeball notification bot that alerts when an ingest has finished
and there are objects with rank > 4 in the eyeball and fast track lists.

"""
from atlasapiclient import client as atlasapiclient
from atlasapiclient.utils import API_CONFIG_FILE
from atlasvras.utils.misc import fetch_vra_dataframe
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import pandas as pd
import yaml
import pkg_resources

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

# Get ATLAS IDs from the eyeball list -> set eyeball
get_ids_from_eyeball = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='eyeball',
                                         get_response=True
                                         )

set_eyeball_ids = set(get_ids_from_eyeball.atlas_id_list_int)

# Get ATLAS IDS from the fast track eyeball list -> set fast track
get_ids_from_fasttrack = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='fasttrack',
                                         get_response=True
                                         )
set_fasttrack_ids = set(get_ids_from_fasttrack.atlas_id_list_int)

# Get VRA scores table since DATETHRESHOLD to chose
# Using the oldest data in the To Do list to set the datethreshold
todo_list = atlasapiclient.RequestVRAToDoList(api_config_file=API_CONFIG_FILE)
todo_list.get_response()
todo_df = pd.DataFrame(todo_list.response_data).sort_values('timestamp')
DATETHRESHOLD= todo_df.timestamp.iloc[0]


vra_df = fetch_vra_dataframe(datethreshold=DATETHRESHOLD)
# NEED TO ENSURE WE ARE LOOKING AT THE LAST VRA SCORE GIVEN
vra_df = vra_df[vra_df.apiusername=='vra'] # only looks at rows that the VRA dded
vra_df = vra_df[vra_df.rank_alt1.isna()] # remove all the rows with alternate ranks, where rank == NaN
vra_df.drop_duplicates('transient_object_id', keep='last', inplace=True) # remove duplicates and keep last rank

# set_hi_vra_rank : ATLAS IDS from vra scores tbale where rank >= EYEBALL_THRESHOLD
set_hi_vra_rank_ids = set(vra_df[vra_df['rank'] >= EYEBALL_THRESHOLD].transient_object_id)

# set_fasttrack_hi_rank = intersection set fast track and set hi vra rank
set_fasttrack_hi_rank_ids = set_fasttrack_ids.intersection(set_hi_vra_rank_ids)

# set_eyeball_hi_rank = intersection set eyeball and set hi vra rank
#set_eyeball_hi_rank_ids = set_eyeball_ids.intersection(set_hi_vra_rank_ids)
set_eyeball_hi_rank_ids = set_hi_vra_rank_ids.intersection(set_eyeball_ids)

# Counting the number of events in the Galactic candidate list
get_ids_from_galcand = atlasapiclient.RequestATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='galcand',
                                         get_response=True
                                         )
n_gal_candidates = len(get_ids_from_galcand.response_data)

# OUTPUTS
bot_message = f"*Ingest Complete*\n"

if len(set_fasttrack_ids) == 0 and len(set_eyeball_hi_rank_ids) == 0:
    # If nothing in Fast track or eyeball end the script without sending a message
    exit(1)

if len(set_fasttrack_ids)>0:
    bot_message += (f":bell: {len(set_fasttrack_hi_rank_ids)} objects with rank > {EYEBALL_THRESHOLD}. "
                f"({len(set_fasttrack_ids) - len(set_fasttrack_hi_rank_ids)} with low ranks): :link:"
                f"<{URL_BASE}followup_quickview/8/|Fast Track List>\n\n")

if len(set_eyeball_hi_rank_ids)>0:
    bot_message += (f":boom:  {len(set_eyeball_hi_rank_ids)} objects with rank > {EYEBALL_THRESHOLD}. :link: "
               f"<{URL_BASE}followup_quickview/4/?vra__gte={EYEBALL_THRESHOLD}&sort=-vra| Extragalactic Candidates>\n"
               )

if n_gal_candidates> 0:
    bot_message += (f":stars:  {n_gal_candidates} objects. "
                f":link:"
                f"<{URL_BASE}followup_quickview/12/| Galactic Candidates>\n\n")

# SUMMONING THE SLACK BOT
client = WebClient(token=SLACK_TOKEN)

try:
    response = client.chat_postMessage(
        channel="#vra",
        text=bot_message
    )
except SlackApiError as e:
    print(f"Error sending message: {e.response['error']}")
