import numpy as np
import pytest
import atlasapiclient as atlasapi
import pkg_resources
import os
from atlasvras.utils.jsondata import JsonData

data_path = pkg_resources.resource_filename('atlasvras', 'data')
API_CONFIG_FILE = os.path.join(data_path,'api_config_MINE.yaml')


class TestJsonData():
    test_file = '1000005291314656200_sn.json'
    filename_sn = os.path.join(data_path, test_file)
    json_data_sn = JsonData(filename=filename_sn)

    def test_instanciation_from_response(self):
        request_source = atlasapi.client.RequestSingleSourceData(api_config_file=API_CONFIG_FILE,
                                                          atlas_id='1103337110432157700',
                                                          get_response=True
                                                          )
        JsonData(request_source.response[0])

    def test_instanciation_from_bad_response(self):
        request_source = atlasapi.client.RequestSingleSourceData(api_config_file=API_CONFIG_FILE,
                                                          atlas_id='1103337110432157700',
                                                          get_response=True
                                                          )
        with pytest.raises(AssertionError):
            JsonData(request_source.response)

    def test_values_sn(self):
        lc_mag = self.json_data_sn.get_values(['lc', 'mag'])
        assert np.isclose(lc_mag[0], -18.22), f"The first mag value for {self.test_file} should be -18.2"


    def test_bad_filename(self):
        bad_filename = 'blaaa'
        with pytest.raises(AssertionError):
            JsonData(filename=bad_filename)