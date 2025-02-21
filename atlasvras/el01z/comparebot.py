"""
Compare Bot
===========
This script compares the ranks of the objects that were processed by the new VRA model
with the ranks of the objects that were processed by the old VRA model. It then sends
a report to the slack channel #vra-dev with the objects that would not have been garbaged
by the old model and the objects that are in the danger zone (rank < 4 in the new model).

It also saves some numbers in a .csv called comparebot_BMOCRABBY.csv in the logs folder.
The columns of that csv are:
- rank_NEW: the rank given by the new model
- rank_OLD: the rank given by the old model
- garbage_flag: whether the object was garbaged (rank = -1)
- timestamp_bot: the timestamp of the bot run

This script is called by comparebot.sh which is in the el01z/bash directory.

Intended use
~~~~~~~~~~
Run in a cron job at least once a day for a month to keep a record of the differences
and to eyeball the objects that are in the danger zone and that may have been good when garbaged.

"""
# IMPORTS
from slack_sdk import WebClient
from atlasvras.utils.misc import fetch_vra_dataframe
import logging
import sys
from datetime import datetime
import numpy as np
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
        SLACK_TOKEN = config['slack_token_el01z']
        URL_BASE = config['base_url']+'candidate/'
        EYEBALL_THRESHOLD = config['eyeball_threshold']
        URL_SLACK = config['url_slack']
    except yaml.YAMLError as exc:
        print(exc)

#####################################################################
# GET THE LAST RUN DATE FROM THE COMMAND LINE ARGUMENTS IN THE BASH SCRIPT
# It grabs the last run date from the logs using regex
#####################################################################
try:
    last_run_date = sys.argv[1]
except IndexError:
    raise IndexError("CL argument not found. Call script with [INCLUDE THE GREP COMMAND I'LL USE IN THE BASH SCRIPT]")

TODAY = datetime.today().strftime('%Y-%m-%d')

#################
# CONFIG LOGGING
#################
logging.basicConfig(level=logging.INFO,
                    # Set the logging level to DEBUG (you can change it as needed)
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    # Define the format of log messages
                    filename=f'{LOG_PATH}/comparebot.log',
                    # Specify the log file
                    filemode='a')  # Set the file mode to 'w' for writing (change as needed)

# Write in the log that we are starting the script
logging.info("Starting the script - last run date: " + last_run_date)

# FETCH THE VRA DATAFRAME
vra_df = fetch_vra_dataframe(datethreshold=last_run_date)
logging.info("Fetched the VRA datarame")
if vra_df.empty:
    logging.info("DataFrame empty - Finished")
    sys.exit()

vra_df.set_index('transient_object_id', inplace=True)
# Remove all the debug rows
vra_df = vra_df[vra_df.debug == False]

########################################################
# GRAB SOME SUBSETS OF THE DATAFRAME TO MAKE THE COMPARISON
########################################################

#  Get the IDs of the objects that have a rank from the old model
old_model_ids = set(vra_df[~vra_df.rank_alt1.isna()].index)
#vra_df.set_index('transient_object_id', inplace=True)
vra_df = vra_df.loc[list(old_model_ids)]

# Data frame that excludes all human made decisions
vra_decisions_df = vra_df[(vra_df.apiusername == 'vra')]

# Dataframe that contains all the rows corresponding to objects that were garbaged
vra_garbaged = vra_decisions_df[vra_decisions_df['rank'] ==-1]
list_garbaged = list(set(vra_garbaged.index))

# Vra for all the objects that were dealth with by NEW model
# excludes the rows corresponding to crossmatching, garbaging and human decisions
vra_df_new_ranks = vra_decisions_df[(vra_decisions_df['rank']!=-1)
                                    & (vra_decisions_df.rank_alt1.isna())
                                    & (vra_decisions_df['rank'] != 10)]

# Vra for all the objects that were dealth with by OLD model
vra_df_old_ranks = vra_decisions_df[(vra_decisions_df['rank']!=-1)
                                    & (~vra_decisions_df.rank_alt1.isna())
                                    & (vra_decisions_df['rank'] != 10)]

####################################
# MAKING THE COMPARISON DATAFRAME
####################################

comparison_df = vra_df_new_ranks[['rank']].join(vra_df_old_ranks.rank_alt1
                                                ).join(vra_garbaged['rank'],
                                                       rsuffix='deleted')

comparison_df.columns = ['rank_NEW', 'rank_OLD', 'garbage_flag']
comparison_df.garbage_flag =( comparison_df.garbage_flag == -1)
comparison_df['timestamp_bot'] = TODAY

##############
# SAVE TO FILE
##############
# Append this to the file where we save the comparison (in the logs folder)
comparison_df.to_csv(f'{LOG_PATH}/comparebot_CRABBYDUCK.csv',
                     header=False, mode='a', index=True)


#########################
# SEND THE REPORT TO SLACK
#########################
# Get the IDs of the objects that would not have been garbaged by the old model
would_not_be_garbaged= vra_df_old_ranks.loc[vra_garbaged.index
                                                                            ][vra_df_old_ranks.loc[vra_garbaged.index
                                                                                                                ].rank_alt1>4].index
# Get the IDs of the objects that are in the danger zone
danger_zone_ids = set(comparison_df[(comparison_df.rank_NEW<4)
                                    & (comparison_df.rank_OLD>4)].index)

# Make the text of the message
TEXT_REPORT = "*Would not have been garbaged by previous VRA version*\n"
for atlas_id in np.unique(would_not_be_garbaged):
    TEXT_REPORT+=f"- <https://star.pst.qub.ac.uk/sne/atlas4/candidate/{atlas_id}|{atlas_id}>:\n"

TEXT_REPORT+="\n*Danger Zone*\n"
for atlas_id in danger_zone_ids:
    TEXT_REPORT += f"- <https://star.pst.qub.ac.uk/sne/atlas4/candidate/{atlas_id}|{atlas_id}>:\n"

logging.info("Sending the report to slack")

# Send the message to slack
client = WebClient(token=SLACK_TOKEN)
client.chat_postMessage(
  channel="#vra-dev",
  text=TEXT_REPORT,
)#"C0842K2QZS8",

# Need the Finished keyword so the next script can find last run date
# (that's how the regex is set up)
logging.info("Finished")