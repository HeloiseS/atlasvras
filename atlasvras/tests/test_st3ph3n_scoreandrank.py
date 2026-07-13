import numpy as np
import pkg_resources
import os
from atlasvras.utils.jsondata import JsonData
from atlasvras.st3ph3n.dataprocessing import (make_day1_lcfeatures,
                                              make_contextual_features,
                                              make_dayN_lcfeatures,
                                              LightCurvePipes
                                              )
from atlasvras.utils.exceptions import VRASaysNo
from atlasvras.st3ph3n.scoreandrank import ScoreAndRank
import pytest

data_path = pkg_resources.resource_filename('atlasvras', 'data')
test_file = '1000005291314656200_sn.json'
filename_sn = os.path.join(data_path, test_file)


class TestScoreAndRank():

    # KNOWN FAILURE (2026-07-13): test_day1 and test_dayN below fail with
    # "ValueError: X has N features, but ... is expecting M features". Root cause:
    # make_day1_lcfeatures now produces 8 LC features (added DET_mag_median_min5d)
    # but the 'crabby' model here was trained on the old 7. Switching to the 'duck'
    # model (scoreandrank.py's actual default) doesn't fully fix it either -- duck
    # expects 8 LC features but a reduced context_feature_columns set (only CV,
    # missing SN/NT/ORPHAN/UNCLEAR). Needs a model/feature-pipeline reconciliation
    # decision (retrain, or trim context_feature_columns, or pick+fix one model).
    def test_day1(self):
        atlas_json = JsonData(filename=filename_sn)
        lc_pipes = LightCurvePipes(atlas_json_data=atlas_json)
        lc_pipes.add_dayN_column()
        day1features = make_day1_lcfeatures(lc_pipes)
        features = day1features + make_contextual_features(atlas_json_data=atlas_json)

        sar = ScoreAndRank(np.atleast_2d(features), model_type='day1', model_name='crabby')

    def test_dayN(self):
        ## Make the day1 features (LC and contextual)
        atlas_json = JsonData(filename=filename_sn)
        lc_pipes = LightCurvePipes(atlas_json_data=atlas_json)
        lc_pipes.add_dayN_column()
        day1features = make_day1_lcfeatures(lc_pipes) + make_contextual_features(atlas_json_data=atlas_json)

        ## Make the dayN LC features
        lc_pipes = LightCurvePipes(atlas_json_data=atlas_json,
                                   phase_bounds=(-5,15),
                                   make_history=False
                                   )
        lc_pipes.add_dayN_column()

        ## Put together the dayN features with the day1 features
        features = make_dayN_lcfeatures(lcpipes=lc_pipes) + day1features
        sar = ScoreAndRank(np.atleast_2d(features), model_type='dayN', model_name='crabby')

    def test_parse_feature_list(self):
        with pytest.raises(VRASaysNo):
            sar = ScoreAndRank(features=['blaa'], model_type='day1', model_name='crabby')
