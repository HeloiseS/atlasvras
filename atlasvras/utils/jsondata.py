"""
:Description: Utility class to handle the JSON data format return by the ATLAS API
:Creation Date: 2024-11-14
:Last Update: 2024-11-14

Classes
=======
JsonData
    Base object to load and interact with a .json data file for an ATLAS transient event.
"""
import os
import pkg_resources
import json
import numpy as np
import pandas as pd
from atlasvras.utils import exceptions


data_path = pkg_resources.resource_filename('atlasvras', 'data')
API_CONFIG_FILE = os.path.join(data_path,'api_config_MINE.yaml')


class JsonData(object):
    DEBUG_ASSISTANT_JSON = ("DEBUG ASSISTANT: The ATLAS API returns a list of responses (json dictionaries) even if "
                            "only one source (response) is requested. "
                            "Instead of providing response=my_response, try response=my_response[0]. ")

    def __init__(self,
                 response: dict = None,
                 filename: str = None
                 ):
        """
        Base object to load and interact with a .json data file for an ATLAS transient event.
        """

        if response is not None and filename is None:
            assert isinstance(response, dict), f"The response should be in JSON format. {self.DEBUG_ASSISTANT_JSON}"
            self.data = response
        elif filename is not None and response is None:
            assert os.path.exists(filename), "The filename does not exist"
            self.filename = filename
            self._open_json_file()

        self.atlas_id = self.data['object']['id']
        self.fp_uJy = None
        self.fp_duJy = None

    def _open_json_file(self):
        with open(self.filename) as input_file:
            self.data = json.load(input_file)

    def save_to_json(self, output_dir: str):
        output_file = os.path.join(output_dir, f"{self.atlas_id}.json")
        with open(output_file, 'w') as output:
            json.dump(self.data, output)

    def get_values(self, keys: [str, str] = ['lc', 'mjd']) -> np.ndarray:
        """
        Returns an array of values for series values that are located in individual sub-dictionaries of the JSON data.
        For example light curve has one dictionary per data point and each dictionary has keys: mjd, mag, magerr, filter etc.
        So to recover the mjd or the mag in a single numpy array we need to do list comprehension

        :param keys: [str, str] - will return an array of values located at [key1][key2].
        """
        # TODO: find a better way to explain what's going on above
        # TODO: need to point to documentation for the format of the JSON data (which I need to write)
        try:
            return np.array([self.data[keys[0]][i][keys[1]] for i in range(len(self.data[keys[0]]))])
        except KeyError as e:
            raise exceptions.VRAKeyError(f"KeyError: {e} | One or both of the keys provided are invalid")

    def make_sherlock_features(self):
        self.sherlock_features = []
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'SN']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'NT']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'ORPHAN']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'CV']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'UNCLEAR']
        return self.sherlock_features