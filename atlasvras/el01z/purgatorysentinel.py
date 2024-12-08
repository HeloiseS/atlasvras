from atlasapiclient import client as atlasapiclient
from atlasapiclient.utils import API_CONFIG_FILE

from atlasvras.st3ph3n.slackbot import URL_BASE, EYEBALL_THRESHOLD
from atlasvras.utils.misc import fetch_vra_dataframe
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import pandas as pd
from datetime import datetime
import logging
import sys
import pkg_resources
import yaml

BOT_CONFIG_FILE = pkg_resources.resource_filename('atlasvras', 'data/bot_config_MINE.yaml')

with open(BOT_CONFIG_FILE, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        LOG_PATH = config['log_path']
        SLACK_TOKEN = config['slack_token_el01z']
        URL_BASE = config['base_url']
        EYEBALL_THRESHOLD = config['eyeball_threshold']
        URL_SLACK = config['url_slack']
    except yaml.YAMLError as exc:
        print(exc)


# Get the last run date from the command line arguments. This will be handled by the
# bash script that will call this python script.
try:
    last_run_date = sys.argv[1]
except IndexError:
    raise IndexError("CL argument not found. Call script with [INCLUDE THE GREP COMMAND I'LL USE IN THE BASH SCRIPT]")
# last_run_date = '2024-09-13'

TODAY = datetime.today().strftime('%Y-%m-%d')
# Configure logging
logging.basicConfig(level=logging.INFO,
                    # Set the logging level to DEBUG (you can change it as needed)
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    # Define the format of log messages
                    filename=f'{LOG_PATH}/purgatorysentinel.log',
                    # Specify the log file
                    filemode='a')  # Set the file mode to 'w' for writing (change as needed)

# Write in the log that we are starting the script
logging.info("Starting the script - last run date: " + last_run_date)

### Get all objects in Eyeball List right now
get_ids_from_eyeball = atlasapiclient.GetATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='eyeball',
                                         get_response=True
                                         )

# Use oldest data in ToDo list to set the datethreshold
todo_list = atlasapiclient.RequestVRAToDoList(api_config_file=API_CONFIG_FILE)
todo_list.get_response()
# if the response is empty list  we want to exit the script
if not todo_list.response:
    logging.info("ToDo List is empty - Finished")
    sys.exit()

DATETHRESHOLD= pd.DataFrame(todo_list.response).sort_values('timestamp').timestamp.iloc[0]
logging.info("Fetched the TODO List dataframe")

vra_df = fetch_vra_dataframe(datethreshold=DATETHRESHOLD)
vra_df.set_index('transient_object_id', inplace=True)

# Crop df so only objects in eyeball list are left
vra_df=vra_df.loc[get_ids_from_eyeball.atlas_id_list_int]
logging.info("Got the VRA dataframe")

# add a column recording the first timestamp for each object
vra_df_w1st_time = vra_df.join(vra_df.reset_index().drop_duplicates('transient_object_id',
                                                                                                                    keep='first').set_index('transient_object_id'
                                                                                                                                                            )['timestamp'],
                                                    rsuffix='_first')

# PANDAS SHENANIGANS TO GET THE PHASE IN DAYS
# Explanation: We want to add a column that is the delta time between first and current timestamp
# 1. We need to convert to Timestamps before we take the Timedelta
# 2. You can't do it in bulk because Timestamp takes one value at a time so we use a list comprehension
# 3. We iterate over i the iloc (literally just the row number)
# 4. Since with Timedelta we'd have to do the list comprehension as well I'm doing both the conversions
# of both timestamp and timestamp_first AND putting them in Timedelta and getting the .days in one line
# So it looks terrifying but I'm just ripping off the bandaid
phase_days = [pd.Timedelta(
                          pd.Timestamp(TODAY, tz='UTC'
                                      )-pd.Timestamp(vra_df_w1st_time.timestamp_first.iloc[i]
                                                    )
                                      ).days
                          for i in range(vra_df_w1st_time.shape[0])
                         ]

vra_df_w1st_time['phase_in_days'] = phase_days

# I'm doing  a bit longer than 15 in case time zone shenanigans i didn't think of
stuck_in_purgatory = vra_df_w1st_time[vra_df_w1st_time.phase_in_days>16].index.unique().values
# output to csv the stuck in purgatory ids with today's date
stuck_in_purgatory_df = pd.DataFrame(stuck_in_purgatory)
stuck_in_purgatory_df['timestamp']=TODAY
stuck_in_purgatory_df.to_csv(f'{LOG_PATH}/stuck_in_purgatory.csv',
                                header=False, mode='a', index=False)


TEXT_REPORT = "*Stuck in Purgatory*\n"
for atlas_id in stuck_in_purgatory:
    TEXT_REPORT+=f"- <{URL_BASE}{atlas_id}|{atlas_id}>\n"

logging.info("Sending the report to slack")

client = WebClient(token=os.getenv('SLACK_TOKEN_el01z'))
client.chat_postMessage(
  channel="#vra-dev",
  text=TEXT_REPORT,
)#"C0842K2QZS8",

logging.info("Finished")
