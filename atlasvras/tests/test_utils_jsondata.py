import numpy as np
import pytest
import atlasapiclient as atlasapi
import pkg_resources
import os
from atlasvras.utils.jsondata import JsonData, JsonDataFromServer
from atlasvras.utils.misc import API_CONFIG_FILE

data_path = pkg_resources.resource_filename('atlasvras', 'data')


class TestJsonData():
    test_file = '1000005291314656200_sn.json'
    filename_sn = os.path.join(data_path, test_file)
    json_data_sn = JsonData(filename=filename_sn)

    def test_instanciation_from_filename(self):
        JsonData(filename=self.filename_sn)

    def test_instanciation_from_response(self):
        request_source = atlasapi.client.RequestSingleSourceData(api_config_file=API_CONFIG_FILE,
                                                          atlas_id='1103337110432157700',
                                                          get_response=True
                                                          )
        JsonData(request_source.response_data[0])

    def test_instanciation_from_bad_response(self):
        request_source = atlasapi.client.RequestSingleSourceData(api_config_file=API_CONFIG_FILE,
                                                          atlas_id='1103337110432157700',
                                                          get_response=True
                                                          )
        with pytest.raises(AssertionError):
            JsonData(request_source.response_data)

    def test_values_sn(self):
        lc_mag = self.json_data_sn.get_values(['lc', 'mag'])
        assert np.isclose(lc_mag[0], -18.22), f"The first mag value for {self.test_file} should be -18.2"


    def test_bad_filename(self):
        bad_filename = 'blaaa'
        with pytest.raises(AssertionError):
            JsonData(filename=bad_filename)


class TestJsonDataFromServer():
    def test_instanciation(self):
        data = JsonDataFromServer(atlas_id='1103337110432157700')

    def test_instanciation_with_good_int(self):
        data = JsonDataFromServer(atlas_id=1103337110432157700)

    def test_instanciation_with_bad_id(self):
        with pytest.raises(AssertionError):
            data = JsonDataFromServer(atlas_id='blaa')