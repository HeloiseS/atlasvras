import os
from joblib import load
from glob import glob
import numpy as np

# TODO: add test -> run for that SN i'm using the data processing stuff so can run locally
class ScoreAndRank(object):


    def __init__(self, features, model_type, model_name='crabby'):
        """
        Pipes to score and rank objects based on their features

        :param features: pd.DataFrame
            DataFrame of features. These must be the right kind of features for the specific model,
            you can't just put anything in there. Check the manual
        :param model_type: str
            model type, either 'day1' or 'dayN'
        :param model_name: str
            Family of models to use, e.g. Arin, BMO
        """
        assert model_type in ['day1', 'dayN'], 'model_type must be "day1" or "dayN"'
        self.model_type = model_type
        # TODO: check model name is valid
        self.model_name = model_name
        self.model_path = os.path.join('models',  self.model_type, self.model_name)
        self.features = features #TODO: check acceptable type and columsn and stugg that will depends on model nbame probably needs to be in a method

        self.gal_model = load(glob(os.path.join(self.model_path, 'gal*')[0]))
        self.real_model = load(glob(os.path.join(self.model_path, 'real*')[0]))

        self.make_predictions()


    def make_predictions(self):
        self.real_scores = self.real_model.predict_proba(self.features)
        self.gal_scores = self.gal_model.predict_proba(self.features)

    def calculate_rank(self, fudge_factor=0.4, max_score=10):
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