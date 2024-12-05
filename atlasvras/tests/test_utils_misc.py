import pytest
import pkg_resources
import os
from atlasvras.utils.misc import fetch_vra_dataframe, API_CONFIG_FILE
from atlasvras.utils.exceptions import VRASaysNo
import datetime

today = datetime.date.today()
today = today.strftime('%Y-%m-%d')

data_path = pkg_resources.resource_filename('atlasvras', 'data')

class TestFetchDataFrame():
    def test_runs_with_good_input(self):
        fetch_vra_dataframe(datethreshold=today,
                                        API_CONFIG_FILE=API_CONFIG_FILE)
    def test_no_datethreshold(self):
        with pytest.raises(VRASaysNo):
            fetch_vra_dataframe(datethreshold=None,
                                        API_CONFIG_FILE=API_CONFIG_FILE)