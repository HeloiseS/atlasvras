#!/usr/bin/bash

export PYTHONPATH=/usr/local/ps1code/gitrelease/atlasapiclient:/usr/local/ps1code/gitrelease/atlasvras
export CONFIG_ATLASAPI=/usr/local/ps1code/gitrelease/atlasapiclient/atlasapiclient/config_files/api_config_MINE.yaml

export PYTHON="/usr/local/swtools/python/atls/anaconda3/envs/vra/bin/python"
export CODEBASE="/usr/local/ps1code/gitrelease/atlasvras/atlasvras/el01z"
export LOGBASE="/db5/tc_logs/atlas4/vralogs"

$PYTHON $CODEBASE/garbagetnsbot.py  #> /tmp/whathappened_purgatorysentinel.log 2>&1
