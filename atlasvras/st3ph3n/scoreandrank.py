import os
from joblib import load
from glob import glob
import numpy as np
import pkg_resources
from atlasvras.st3ph3n.dataprocessing import day1_lc_feature_columns, context_feature_columns, dayN_lc_feature_columns
from atlasvras.utils.exceptions import VRASaysNo

MODELS_PATH = pkg_resources.resource_filename('atlasvras', 'st3ph3n/models')

class ScoreAndRank(object):

    def __init__(self, features, model_type, model_name='duck'):
        """
        Pipes to calculate the scores and ranks (mostly used in production)

        Parameters
        ----------
        features : 2D np.array
            Features to be scored and ranked. MUST BE 2D to go into the sklearn models. Must also be inthe right order.
            For day1 models this is [day1_lc_features, context_features], for dayN models this is [dayN_lc_features, day1_lc_features, context_features]
        model_type : str
            Either 'day1' or 'dayN'.
        model_name : str
            Name of the model to use. Default is 'crabby' for this version of the code.
        """
        assert model_type in ['day1', 'dayN'], 'model_type must be "day1" or "dayN"'
        self.model_type = model_type
        self.model_name = model_name
        self.model_path = os.path.join(MODELS_PATH,  self.model_name, self.model_type)
        gal_model = glob(os.path.join(self.model_path, 'gal*'))[0]
        real_model = glob(os.path.join(self.model_path, 'real*'))[0]
        assert os.path.isfile(gal_model), 'Galactic model not found'
        assert os.path.isfile(real_model), 'Real model not found'

        # check features is 2D array if nto make it 2D
        if isinstance(features, list):
            raise VRASaysNo('Features must be a 2D array where axis 0 is the samples and axis 1 is the features')

        self.features = features
        self.gal_model = load(gal_model)
        self.real_model = load(real_model)

        self.make_predictions()


    def make_predictions(self):
        self.real_scores = self.real_model.predict_proba(self.features)
        self.gal_scores = self.gal_model.predict_proba(self.features)

    def calculate_rank(self, fudge_factor=0.5, max_score=10):
        """
        Calculate the (OxQUB) rank from the real and galactic scores. This is currently just the distance
        to the (1,0) coordinate (Real and Not Galactic) in our Score Space.
        The fudge factor is a way to change the weight of the real score vs the galactic score.

        :param fudge_factor: float
            Weight of the galactic score relative to the real score. Default is 0.5 is the galactic axis is squished
            by half compared to the real axis.
        """
        raw_ranks = np.sqrt(self.real_scores.T[0]**2 + (fudge_factor*self.gal_scores.T[1])**2)
        max_distance = np.sqrt(fudge_factor**2 + 1)
        self.ranks = (max_distance - raw_ranks) * max_score / max_distance

    @property
    def is_gal_cand(self, fudge_factor=0.9, distance=0.4):
        # TODO: add a test
        """
        If distance to coordinate (1,1) is <= 0.45 then returns True
        """
        d = np.sqrt((self.real_scores.T[0]) ** 2 + fudge_factor ** 2 * (self.gal_scores.T[0]) ** 2)
        return d <= distance
