from slack_sdk import WebClient
import pandas as pd
from datetime import datetime
import pkg_resources
import yaml
import numpy as np

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

TODAY = datetime.today().strftime('%Y-%m-%d')

PATH_TO_TNSXMATCH='/db5/tc_logs/atlas4/garbagexmatch.csv'
xmatches = pd.read_csv(PATH_TO_TNSXMATCH, names=['transient_object_id', 'tns_name', 'timestamp'])
recent_xmatches = xmatches[xmatches.timestamp>=TODAY] #dunno if will work

TEXT_REPORT = ":no_entry_sign: *Garbage-TNS Xmatch in the last week*\n"
for atlas_id in np.unique(recent_xmatches.transient_object_id):
    TEXT_REPORT+=f"<https://star.pst.qub.ac.uk/sne/atlas4/candidate/{atlas_id}/|{atlas_id}>\n"

client = WebClient(token=SLACK_TOKEN)
client.chat_postMessage(
  channel="#vra-dev",
  text=TEXT_REPORT,
)#"C0842K2QZS8",
