# Slack API
from slack_sdk import WebClient
from atlasvras.utils.misc import fetch_vra_dataframe
# generic things
import logging
import sys
from datetime import datetime
import os
# Analysis things
import numpy as np
import pandas as pd

LOG_PATH = '/home/stevance/software/logs/'

####################################################################################
######################### STARTING THE SCRIPT ######################################

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
                    filename=f'{LOG_PATH}/comparebot.log',
                    # Specify the log file
                    filemode='a')  # Set the file mode to 'w' for writing (change as needed)

# Write in the log that we are starting the script
logging.info("Starting the script - last run date: " + last_run_date)

vra_df = fetch_vra_dataframe(datethreshold=last_run_date)
logging.info("Fetched the VRA datarame")
if vra_df.empty:
    logging.info("DataFrame empty - Finished")
    sys.exit()

vra_df.set_index('transient_object_id', inplace=True)
# Remove all the debug rows
vra_df = vra_df[vra_df.debug == False]

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

# Making the comparison dataframe
comparison_df = vra_df_new_ranks[['rank']].join(vra_df_old_ranks.rank_alt1
                                                ).join(vra_garbaged['rank'],
                                                       rsuffix='deleted')

comparison_df.columns = ['rank_NEW', 'rank_OLD', 'garbage_flag']
comparison_df.garbage_flag =( comparison_df.garbage_flag == -1)
comparison_df['timestamp_bot'] = TODAY

# Append this to the file where we save the comparison (in the logs folder)
comparison_df.to_csv(f'{LOG_PATH}/comparebot_BMOCRABBY.csv',
                     header=False, mode='a', index=True)


would_not_be_garbaged= vra_df_old_ranks.loc[vra_garbaged.index
                                                                            ][vra_df_old_ranks.loc[vra_garbaged.index
                                                                                                                ].rank_alt1>4].index

danger_zone_ids = set(comparison_df[(comparison_df.rank_NEW<4)
                                    & (comparison_df.rank_OLD>4)].index)

### SLACK BOT
TEXT_REPORT = "*Would not have been garbaged by previous VRA version*\n"
for atlas_id in np.unique(would_not_be_garbaged):
    TEXT_REPORT+=f"- <https://star.pst.qub.ac.uk/sne/atlas4/candidate/{atlas_id}|{atlas_id}>:\n"

TEXT_REPORT+="\n*Danger Zone*\n"
for atlas_id in danger_zone_ids:
    TEXT_REPORT += f"- <https://star.pst.qub.ac.uk/sne/atlas4/candidate/{atlas_id}|{atlas_id}>:\n"

logging.info("Sending the report to slack")

client = WebClient(token=os.getenv('SLACK_TOKEN_el01z'))
client.chat_postMessage(
  channel="#vra-dev",
  text=TEXT_REPORT,
)#"C0842K2QZS8",

logging.info("Finished")