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
        Utility object to load and interact with Json data from the ATLAS api (either as a dictionary or from a filename).

        Parameters
        ----------
        response : dict
            JSON response from the ATLAS API. If provided, the filename parameter should be None.
        filename : str
            Path to the .json file. If provided, the response parameter should be None.
        """

        if response is not None and filename is None:
            assert isinstance(response, dict), f"The response should be in JSON format. {self.DEBUG_ASSISTANT_JSON}"
            self.data = response

        elif filename is not None and response is None:
            assert os.path.exists(filename), "The filename does not exist"
            self.filename = filename
            self._open_json_file()

        self.atlas_id = self.data['object']['id']

    def _open_json_file(self):
        with open(self.filename) as input_file:
            self.data = json.load(input_file)

    def save_to_json(self, output_dir: str):
        output_file = os.path.join(output_dir, f"{self.atlas_id}.json")
        with open(output_file, 'w') as output:
            json.dump(self.data, output)

    def get_values(self, keys: [str, str] = ['lc', 'mjd']) -> np.ndarray:
        """
        Returns a 1D numpy array for a quantity recorded in multiple sub-dictionaries of the JSON data.
        For example light curve has one dictionary per data point and each dictionary has keys: mjd, mag, magerr, filter etc.
        So to recover the mjd or the mag in a single numpy array we need to do list comprehension.


        Parameters
        ----------
        keys : [str, str]
            Two keys to access the desired values in the JSON data.

        """

        # TODO: use pydantic to have an easy way to check the keys and schema?

        try:
            return np.array([self.data[keys[0]][i][keys[1]] for i in range(len(self.data[keys[0]]))])
        except KeyError as e:
            raise exceptions.VRAKeyError(f"KeyError: {e} | One or both of the keys provided are invalid")

    def make_sherlock_features(self):
        """
        Creates a list of the boolean flags for the SN, NT, ORPHAN, CV and UNCLEAR sherlock classifications

        Returns
        -------
        sherlock_features : list
            List of boolean flags for the sherlock classifications
        """

        self.sherlock_features = []
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'SN']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'NT']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'ORPHAN']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'CV']
        self.sherlock_features = self.sherlock_features + [self.data['object']['sherlockClassification'] == 'UNCLEAR']
        return self.sherlock_features