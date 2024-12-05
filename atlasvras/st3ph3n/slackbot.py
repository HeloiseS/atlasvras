from atlasapiclient import client as atlasapiclient
from atlasapiclient.utils import API_CONFIG_FILE
from atlasvras.utils.misc import fetch_vra_dataframe
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

EYEBALL_THRESHOLD = 4
URL_BASE = 'https://star.pst.qub.ac.uk/sne/atlas4/'
# Get ATLAS IDs from the eyeball list -> set eyeball
get_ids_from_eyeball = atlasapiclient.GetATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='eyeball',
                                         get_response=True
                                         )

set_eyeball_ids = set(get_ids_from_eyeball.atlas_id_list_int)

# Get ATLAS IDS from the fast track eyeball list -> set fast track
get_ids_from_fasttrack = atlasapiclient.GetATLASIDsFromWebServerList(api_config_file= API_CONFIG_FILE,
                                         list_name='fasttrack',
                                         get_response=True
                                         )
set_fasttrack_ids = set(get_ids_from_fasttrack.atlas_id_list_int)

# Get VRA scores table since DATETHRESHOLD to chose
# TODO: when have bots that highlight objects in purgatory we can set this dynamicaly to e.g. last 2 months
DATETHRESHOLD = '2024-07-09' # set to oldest object sin tcs_vra_todo table at time of writing
vra_df = fetch_vra_dataframe(datethreshold=DATETHRESHOLD)

# set_hi_vra_rank : ATLAS IDS from vra scores tbale where rank >= EYEBALL_THRESHOLD
set_hi_vra_rank_ids = set(vra_df[vra_df['rank'] >= EYEBALL_THRESHOLD].transient_object_id)

# set_fasttrack_hi_rank = intersection set fast track and set hi vra rank
set_fasttrack_hi_rank_ids = set_fasttrack_ids.intersection(set_hi_vra_rank_ids)

# set_eyeball_hi_rank = intersection set eyeball and set hi vra rank
set_eyeball_hi_rank_ids = set_eyeball_ids.intersection(set_hi_vra_rank_ids)

# OUTPUTS: len(set_fasttrack_hi_rank), len(set_eyeball_hi_rank)
bot_message = (f"*Ingest Complete*\n"
               f":bell: {len(set_fasttrack_hi_rank_ids)} objects with rank > {EYEBALL_THRESHOLD}. "
               f"({len(set_fasttrack_ids) - len(set_fasttrack_hi_rank_ids)} with low ranks): :link:"
               f"<{URL_BASE}followup_quickview/8/|Fast Track List>\n\n"
               f":eye:  {len(set_eyeball_hi_rank_ids)} objects with rank > {EYEBALL_THRESHOLD}. :link: "
               f"<{URL_BASE}followup_quickview/4/?vra__gte=4.0&sort=-vra|Eyeball List>\n"
               )

# SUMMONING THE SLACK BOT
client = WebClient(token=os.getenv('SLACK_TOKEN'))

try:
    response = client.chat_postMessage(
        channel="#bot-test",
        text=bot_message
    )
except SlackApiError as e:
    print(f"Error sending message: {e.response['error']}")
