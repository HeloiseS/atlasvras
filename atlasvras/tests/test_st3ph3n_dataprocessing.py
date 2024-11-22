import pandas as pd

from atlasvras.utils.jsondata import JsonData
from atlasvras.utils.exceptions import VRASaysNo, VRAWarning
from atlasvras.st3ph3n.dataprocessing import (make_detection_table,
                                              make_non_detection_table,
                                              LightCurvePipes,
                                              make_day1_lcfeatures,
                                              make_contextual_features
                                              )
import pkg_resources
import os
import pytest

data_path = pkg_resources.resource_filename('atlasvras', 'data')
test_file = '1000005291314656200_sn.json'
filename_sn = os.path.join(data_path, test_file)

# ##################################################### #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ##################################################### #

class TestMakeDetectionTable():
    def test_make_detection_table(self):
        json_data = JsonData(filename=filename_sn)
        detections = make_detection_table(json_data)
        assert isinstance(detections, pd.DataFrame), 'The output must be a pandas DataFrame'
        assert detections.shape[0] == 21, 'This dataframe should have 21 rows'
        assert detections.columns.tolist() == ['mjd', 'mag', 'magerr', 'ra', 'dec', 'band', 'det'], 'The columns should be mjd, mag, magerr, ra, dec, band, det'


class TestMakeNonDetectionTable():
    def test_make_non_detection_table(self):
        json_data = JsonData(filename=filename_sn)
        non_detections = make_non_detection_table(json_data)
        assert isinstance(non_detections, pd.DataFrame), 'The output must be a pandas DataFrame'
        assert non_detections.shape[0] == 2991, 'This dataframe should have 2991 rows'
        assert non_detections.columns.tolist() == ['mjd', 'mag', 'magerr', 'ra', 'dec', 'band', 'det'], 'The columns should be mjd, mag, magerr, ra, dec, band, det'

class TestMakeDay1LCFeatures():
    def test_make_day1_lcfeatures(self):
        atlas_json = JsonData(filename=filename_sn)
        lc_pipes = LightCurvePipes(atlas_json_data=atlas_json)
        lc_pipes.add_dayN_column()
        day1features = make_day1_lcfeatures(lc_pipes)
        assert len(day1features) == 7, "There are 7 day1 LC features in this current version of the code"

    def test_make_day1_lcfeatures_wrong_input_object(self):
        with pytest.raises(AssertionError):
            make_day1_lcfeatures('blaa')

    def test_make_day1_lcfeatures_no_dayN_col(self):
        with pytest.raises(AssertionError):
            atlas_json = JsonData(filename=filename_sn)
            lc_pipes = LightCurvePipes(atlas_json_data=atlas_json)
            day1features = make_day1_lcfeatures(lc_pipes)


class TestMakeContextualFeatures():
    def test_make_conextual_features(self):
        atlas_json = JsonData(filename=filename_sn)
        make_contextual_features(atlas_json_data=atlas_json)

# ##################################################### #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~ CLASSES ~~~~~~~~~ CLASSES ~~~~~~~~ CLASSES ~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ##################################################### #


class TestLightCurvePipes():
    def test_standard_instanciation(self):
        json_data = JsonData(filename=filename_sn)
        lc_pipes = LightCurvePipes(atlas_json_data=json_data)
        assert isinstance(lc_pipes.detections, pd.DataFrame), 'The detections must be a pandas DataFrame'
        assert isinstance(lc_pipes.non_detections, pd.DataFrame), 'The non detections must be a pandas DataFrame'
        assert isinstance(lc_pipes.lightcurve, pd.DataFrame), 'The light curve must be a pandas DataFrame'
        assert lc_pipes.lightcurve.shape[0] == lc_pipes.detections.shape[0] + lc_pipes.non_detections.shape[0], 'The light curve should have the same number of rows as detections + non detections'
        assert lc_pipes.lightcurve.phase_init.min() > -100, 'The minimum is -100'
        assert lc_pipes.lightcurve.phase_init.max() < 16, 'The max phase is 16'
        assert isinstance(lc_pipes.history, pd.DataFrame), 'The history must be a pandas DataFrame'

    def test_different_phase_bounds(self):
        json_data = JsonData(filename=filename_sn)
        lc_pipes = LightCurvePipes(atlas_json_data=json_data, phase_bounds=(-10,2))
        assert lc_pipes.lightcurve.phase_init.min() > -10, 'The minimum is -10 now'
        assert lc_pipes.lightcurve.phase_init.max() < 2, 'The max phase is 5 now'

    def test_bad_phase_bounds(self):
        json_data = JsonData(filename=filename_sn)
        with pytest.raises(VRAWarning):
            lc_pipes = LightCurvePipes(atlas_json_data=json_data, phase_bounds=(1,3))
        with pytest.raises(VRASaysNo):
            lc_pipes = LightCurvePipes(atlas_json_data=json_data, phase_bounds=(-2,-10))
