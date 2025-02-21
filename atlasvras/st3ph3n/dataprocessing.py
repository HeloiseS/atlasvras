"""
:Description:
:Creation Date: 2024-11-15
:Last Update: 2025-02-03
"""

import pandas as pd
import numpy as np
from atlasvras.utils.jsondata import JsonData, JsonDataFromServer
from astropy.time import Time
from atlasvras.utils.exceptions import VRASaysNo, VRAWarning
from datetime import datetime, timedelta
from astropy.time import Time
from astropy.coordinates import SkyCoord
from dustmaps.sfd import SFDQuery

# ##################################################### #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~ CONSTANTS ~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ##################################################### #

context_feature_columns = ['ra',
                           'dec',
                           'rb_pix',
                           'z',
                           'photoz',
                           'ebv_sfd',
                           'log10_sep_arcsec',
                           'SN',
                           'NT',
                           'ORPHAN',
                           'CV',
                           'UNCLEAR'
                           ]

day1_lc_feature_columns = ['Nnondet_std',
                                             'Nnondet_mean',
                                             'magdet_std',
                                             'DET_Nsince_min5d',
                                             'NON_Nsince_min5d',
                                             'log10_std_ra_min5d',
                                             'log10_std_dec_min5d']

dayN_lc_feature_columns = ['dayN',
                               'DET_mag_median',
                               'DET_N_today',
                               'DET_N_total',
                               'NON_mag_median',
                               'NON_N_today',
                               'NON_N_total',
                             'max_mag',
                             'max_mag_day'
                           ]

# ##################################################### #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ##################################################### #

def add_dayN_col(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: add a test
    """
    Adds the dayN column to a dataframe (if it has a pre-existing phase_init column).
    dayN is NOT SIMPLY THE INTEGER PART OF phase_init. See Notes for more details.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of the lightcurve data
        The dataframe must have a column called 'phase_init' which is the
        phase w.r.t the date when the alert entered the eyeball list, that is when
        it passed the quality checks and was deemed a real alert
        (see manual and Smith et. al. 2021 for more details).

    Returns
    -------
    pd.DataFrame
        The dataframe with the dayN column added

    Raises
    ------
    AssertionError
        If the dataframe does not have a column called 'phase_init'

    Notes
    -----
    dayN is the integer number of days since the first detection.
    The zeroth day is the day when the observations that triggered the first alert were made.
    Since these observations are made just before the object enters the eyeball list they are NEGATIVE.
    Our zeroth day therefore corresponds to phase_init [-1, 0]. phase_init (0,1] is day 1.
    Consequently dayN is the integer part of phase_init for NEGATIVE phases.
    For positive phases dayN = int(phase_init) + 1. Without this correction day 0 would last  2 days.
    """

    assert 'phase_init' in df.columns, 'The dataframe must have a column called "phase_init"'
    df['dayN'] = df.phase_init.astype(int)
    df['dayN'] = [df.dayN.iloc[i] + 1 if df.phase_init.iloc[i] > 0 else df.dayN.iloc[i] for i in range(df.shape[0])]
    return df


def make_detection_table(json_data: JsonData) -> pd.DataFrame:
    """
    Takes the ATLAS Json data and puts the detections into a pandas DataFrame

    Parameters
    ----------
    json_data : atlasvras.utils.jsondata.JsonData
        The JsonData object containing the data from the ATLAS API
    """

    detections = pd.DataFrame.from_dict({ 'mjd': json_data.get_values(['lc', 'mjd']),
                                          'mag': json_data.get_values(['lc', 'mag']),
                                          'magerr': json_data.get_values(['lc', 'magerr']),
                                          'ra': json_data.get_values(['lc', 'ra']),
                                          'dec': json_data.get_values(['lc', 'dec']),
                                          'band': json_data.get_values(['lc', 'filter'])}
                                        )

    try:
        detections['det'] = True
    except TypeError:
        pass # TODO: eventually you might want to raise a proper error and stop any process

    return detections


def make_non_detection_table(json_data: JsonData) -> pd.DataFrame:
    """
    Takes the ATLAS Json data and puts the non detections into a pandas DataFrame

    Parameters
    ----------
    json_data : atlasvras.utils.jsondata.JsonData
        The JsonData object containing the data from the ATLAS API
    """

    non_dets = pd.DataFrame.from_dict({ 'mjd': json_data.get_values(['lcnondets', 'mjd']),
                                        'mag': json_data.get_values(['lcnondets', 'mag5sig']),
                                        'magerr': [np.nan]*json_data.get_values(['lcnondets', 'mjd']).shape[0],
                                        'ra': [np.nan] * json_data.get_values(['lcnondets', 'mjd']).shape[0],
                                        'dec': [np.nan] * json_data.get_values(['lcnondets', 'mjd']).shape[0],
                                        'band': json_data.get_values(['lcnondets', 'filter'])}
                                    )
    try:
        non_dets['det'] = False
    except TypeError:
        pass

    return non_dets


def make_day1_lcfeatures(lcpipes):
    """
    Creates a list of the day 1 lightcurve features for a single source

    Parameters
    ----------
    lcpipes: atlasvras.st3ph3n.dataprocessing.LightCurvePipes
        The LightCurvePipes object containing the lightcurve data. Must have a history dataframe with a dayN column.

    Returns
    -------
    list

    Raises
    ------
    AssertionError
    """
    assert isinstance(lcpipes, LightCurvePipes), 'The input must be an instance of LightCurvePipes'
    assert 'dayN' in lcpipes.history.columns, 'the history dataframe must have a dayN column. run .add_dayN_column()'

    # Calculate the number of nondetections in between each detection
    n_nondets = lcpipes.history.groupby(['N_dets'])['det'].apply(lambda x: (x == False).sum())

    # Put our day 1 lightcurve features in a list ORDER MATTERS
    lc_features = [n_nondets.std(),
                        # standard deviation of the number of non detections in between each detection
                        n_nondets.mean(),  # mean of the number of non detections in between each detection
                        lcpipes.history[lcpipes.history.det == True].mag.std(),
                        # standard deviation of the magnitudes of the detections
                        lcpipes.history[lcpipes.history.dayN >= -5].det.sum(),  # N detections since day - 5
                        lcpipes.history[lcpipes.history.dayN >= -5].det.count() - lcpipes.history[
                                                                                                      lcpipes.history.dayN >= -5].det.sum(),
                        # N non dets since day -5 (take total count and subtract N dets)
                        np.log10(lcpipes.history[lcpipes.history.dayN >= -5].ra.std()),
                        np.log10(lcpipes.history[lcpipes.history.dayN >= -5].dec.std())
                        ]
    return lc_features


def make_contextual_features(atlas_json_data: JsonData):
    """
    Makes the contextual features for a single source, including getting the extinction
    from the SFD dust maps

    Parameters
    ----------
    atlas_json_data: atlasvras.utils.jsondata.JsonData
        The JsonData object containing the data from the ATLAS API

    Returns
    -------
    list

    """
    # do extinction
    coords = SkyCoord(str(atlas_json_data.data['object']['ra']),
                      str(atlas_json_data.data['object']['dec']),
                      frame='icrs', unit='deg')
    sfd = SFDQuery()
    ebv = sfd(coords)

    if len(atlas_json_data.data['sherlock_crossmatches']) != 0:
        context_features = [atlas_json_data.data['object']['ra'],
                                 atlas_json_data.data['object']['dec'],
                                 atlas_json_data.data['object']['rb_pix'],
                                 atlas_json_data.data['sherlock_crossmatches'][0]['z'],
                                 atlas_json_data.data['sherlock_crossmatches'][0]['photoz'],
                                 ebv,
                                 np.log10(atlas_json_data.data['sherlock_crossmatches'][0]['separationarcsec'])
                                 ]
    else:
        context_features = [atlas_json_data.data['object']['ra'],
                                 atlas_json_data.data['object']['dec'],
                                 atlas_json_data.data['object']['rb_pix'],
                                 np.nan,
                                 np.nan,
                                 ebv,
                                 np.nan
                                 ]
    context_features = context_features + atlas_json_data.make_sherlock_features()
    return context_features


def max_mag_features_in(lightcurve: pd.DataFrame, atlas_id: str = None) -> tuple:
    """
    Calculates the maximum observed magnitude (and records the time) for a single source.
    Note that it uses the median values and requires the following columns to have been added to the lightcurve dataframe:
    'DET_mag_median', 'dayN'

    That is done in the make_dayN_lcfeatures function before calling this function.
    """
    # ##### CHECKS #### #
    assert 'DET_mag_median' in lightcurve.columns, 'The lightcurve dataframe must have a column called DET_mag_median'
    assert 'dayN' in lightcurve.columns, 'The lightcurve dataframe must have a column called dayN'

    # #### SET UP #### #
    # Initialise lists to store the max magnitude and the day it was observed as well as which day N we are on
    # These are put into a df later - I just find appending lists easiser than dfs
    list_max_mag = []
    list_max_mag_day = []
    list_dayN = []

    # Initialise our max mag to a very high value a.k.a low brightness
    max_mag = 99
    max_mag_day= np.nan

    # #### LOOP OVER EACH DAYN #### #
    for i in range(lightcurve.shape[0]):
        try:
            # If our FIRST observation is a non-detection
            if np.isnan(lightcurve.DET_mag_median.iloc[i]) and max_mag == 99:
                list_max_mag.append(np.nan)  # then max mag is nan
                list_max_mag_day.append(np.nan)

            # If a later observation is a non-detection
            elif np.isnan(lightcurve.DET_mag_median.iloc[i]) and max_mag != 99:
                list_max_mag.append(max_mag)  # max mag stays the same and we just append the same value again
                list_max_mag_day.append(max_mag_day)  # same for the max_mag_day

            # If it IS a detection and it is BRIGHTER than the max mag so far (so LOWER)
            elif lightcurve.DET_mag_median.iloc[i] < max_mag:
                max_mag = lightcurve.iloc[i].DET_mag_median  # we dayN the max mag
                max_mag_day = lightcurve.iloc[i].dayN  # and the day it was observed
                list_max_mag.append(max_mag)  # and append these values to our lists
                list_max_mag_day.append(max_mag_day)

            # If it IS a detection but it is NOT brighter than the max mag so far (so value is GREATER)
            else:
                list_max_mag.append(max_mag)  # max mag stays the same and we just append the same value again
                list_max_mag_day.append(max_mag_day)  # same for the max_mag_day

            # Finally for bookkeeping we append which day N we are on (to make df later)
            list_dayN.append(lightcurve.dayN.iloc[i])

        # NOTE! If we have a SINGLE ROW in our lightcurve dataframe
        # then the syntax above FAILS and give an AttributeError.
        except AttributeError:
            # If we have a single row and it is NOT a detection
            if np.isnan(lightcurve.DET_mag_median):
                list_max_mag.append(np.nan)  # max mag is nan
                list_max_mag_day.append(np.nan)  # and the day of max mag is nan too

            # If we have a single row and it IS a detection
            else:
                max_mag = lightcurve.DET_mag_median  # we set our max_mag and max_mag_day
                max_mag_day = lightcurve.dayN
                list_max_mag.append(max_mag)  # before appending the values to our lists
                list_max_mag_day.append(max_mag_day)

            # Finally for bookkeeping we append which dayN we are on (to make df later)
            list_dayN.append(lightcurve.dayN)
            break

    # #### RETURN #### #

    return list_max_mag, list_max_mag_day, list_dayN


def make_dayN_lcfeatures(lcpipes):
    """
    Makes the dayN lightcurve features for a single source.

    Parameters
    ----------
    lcpipes: atlasvras.st3ph3n.dataprocessing.LightCurvePipes
        The LightCurvePipes object containing the lightcurve data. Must have a history dataframe with a dayN column.
        Also the phase bounds must be (-5, 15) (because I said so).

    Returns
    -------
    list

    """
    assert lcpipes.phase_bounds[0] == -5, 'The lower phase bound must be -5 in these models'
    assert lcpipes.phase_bounds[1] == 15, 'The upper phase bound must be 15 in these models'
    assert 'dayN' in lcpipes.detections.columns, 'The detections dataframe must have a dayN column. Run .add_dayN_column()'

    ## Median mag dataframes
    det_wmed = lcpipes.detections.set_index(['dayN']).join(lcpipes.detections.groupby(['dayN'])['mag'].median(),
                                                           rsuffix='_median'
                                                           )
    det_wmed.reset_index(inplace=True)

    nondet_wmed = lcpipes.non_detections.set_index(['dayN']).join(
        lcpipes.non_detections.groupby(['dayN'])['mag'].median(),
        rsuffix='_median'
        )

    nondet_wmed.reset_index(inplace=True)

    # Median mag for each dayN record
    med_det_perday = det_wmed.groupby(['dayN']
                                      ).max().mag_median.rename(
        'DET_mag_median')  # Here "max" is just a way to get the median as the values are all the same for each dayN rows
    med_nondet_perday = nondet_wmed.groupby(['dayN']
                                            ).max().mag_median.rename('NON_mag_median')

    # Number of detections and non detections for a given dayN
    Ndets_perday = det_wmed.groupby(['dayN']).count().mag.rename('DET_N_today')
    Nnondets_perday = nondet_wmed.groupby(['dayN']).count().mag.rename('NON_N_today')

    # Combine the dayN features and join into a single lightcurve features dataframe
    det_features = pd.concat((med_det_perday, Ndets_perday), axis=1)
    nondet_features = pd.concat((med_nondet_perday, Nnondets_perday), axis=1)
    lightcurve_features = det_features.join(nondet_features, how='outer'
                                            ).reset_index().sort_values('dayN')

    # ### MAKE GLOBAL FEATURES ### #
    # Basically add up the number of detections and non detections for each dayN in our lightcurve
    lightcurve_features['DET_N_total'] = lightcurve_features.cumsum().DET_N_today
    lightcurve_features['NON_N_total'] = lightcurve_features.cumsum().NON_N_today

    # Crop our dataframe to only keep the columns we need

    lightcurve_features = lightcurve_features[
        dayN_lc_feature_columns[:-2]]  # we don't need the max mag features here yet

    # ### MAKE MAX MAG FEATURES ### #
    list_max_mag, list_max_mag_day, list_dayN = max_mag_features_in(lightcurve_features)

    # #### CLEAN UP #### #
    # Make max mag features data frame
    df_max_mag = pd.DataFrame.from_dict({'dayN': np.array(list_dayN),
                                         'max_mag': np.array(list_max_mag),
                                         'max_mag_day': np.array(list_max_mag_day)
                                         })
    df_max_mag.set_index(['dayN'])

    # Join the max mag feature to the other lightcurve features using dayN as the index
    lightcurve_features = lightcurve_features.set_index(['dayN']
                                                        ).join(df_max_mag.set_index(['dayN'])
                                                               ).reset_index(
        'dayN')  # Resets the index so dayN is a column again and gets included in our list when we do to_list() below

    # Finally we record the last row of our data frame into our lc_features list
    return lightcurve_features.iloc[-1].to_list()


# ##################################################### #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~ CLASSES ~~~~~~~~~ CLASSES ~~~~~~~~ CLASSES ~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ##################################################### #

class LightCurvePipes(object):

    def __init__(self,
                 atlas_json_data: JsonData = None,
                 phase_bounds: tuple = (-100, 16),
                 make_history: bool = True
                 ) -> None:
        """
        Pipes to extract LC data from JSON files, make the lightcurve dataframe and history dataframe for a Single Source

        Parameters
        ----------
        atlas_json_data : atlasvras.utils.JsonData
            The ATLAS JsonData object containing the data downloaded using the ATLAS API.  You can't just give JSON data,
            it must be an instance of the JsonData class as we use the methods of that class.

        phase_bounds : tuple
            The lower and upper phase cutoffs for the lightcurve data. The phase is calculated w.r.t the date when the alert

        make_history : bool
            If True, the history dataframe will be created. If False, it will not be created.

        Attributes
        ----------
        atlasjson : atlasvras.utils.JsonData
            The JsonData object containing the data from the ATLAS API
        phase_bounds : tuple
            The lower and upper phase cutoffs for the lightcurve data
        lo_phase_cutoff : float
            The lower phase cutoff
        hi_phase_cutoff : float
            The upper phase cutoff
        detections : pd.DataFrame
            The dataframe containing the detections. Cropped to the phase_bounds.
        non_detections : pd.DataFrame
            The dataframe containing the non detections. Cropped to the phase_bounds.
        lightcurve : pd.DataFrame
            The dataframe containing both the detections and non detections. Ordered by phase_init (or MJD, same result).
            Also cropped to the phase_bounds.
        history : pd.DataFrame
            The dataframe containing the "history" of the object. See docstring of make_history for more details.

        Methods
        -------
        .make_history()
        .add_dayN_column()
        """

        # ### CHECKS AND SET UP ### #
        assert atlas_json_data is not None, 'You must provide an atlasvras.utils.JsonData object'
        if phase_bounds[0] >= phase_bounds[1]:
            raise VRASaysNo('Invalid phase_bounds: The lower phase cutoff must be less than the higher phase cutoff')
        if phase_bounds[0] >0:
            raise VRAWarning('If the lower phase cutoff is positive, the history dataframe will be empty')

        assert  (isinstance(atlas_json_data, JsonData) or isinstance(atlas_json_data, JsonDataFromServer)), 'The atlas_json_data must be an instance of atlasvras.utils.JsonData'
        self.atlasjson = atlas_json_data
        self.phase_bounds = phase_bounds
        self.lo_phase_cutoff = phase_bounds[0]
        self.hi_phase_cutoff = phase_bounds[1]
        # ######################## #

        # ###  MAKE DETS AND NON DETS DATAFRAMES ### #
        self.detections = make_detection_table(self.atlasjson)
        self.non_detections = make_non_detection_table(self.atlasjson)

        # ###  ADD PHASE_INIT COLUMN ### #
        mjd_init = Time(pd.to_datetime(self.atlasjson.data['object']['followup_flag_date'])).mjd
        self.detections['phase_init'] = self.detections['mjd'] - mjd_init
        self.non_detections['phase_init'] = self.non_detections['mjd'] - mjd_init

        # ### CROP TO THE WINDOW OF TIME SPECIFIED ### #
        self.detections = self.detections[(self.detections['phase_init'] < self.hi_phase_cutoff)
                                                            & (self.detections['phase_init'] >= self.lo_phase_cutoff)]
        self.non_detections = self.non_detections[(self.non_detections['phase_init'] < self.hi_phase_cutoff)
                                                            & (self.non_detections['phase_init'] >= self.lo_phase_cutoff)]

        # ### CONCATENATE TO LIGHTCURVE ### #
        self.lightcurve = pd.concat([self.detections, self.non_detections],
                                    ignore_index=False).sort_values(by='phase_init')

        self.history = None
        if make_history:
            self.make_history()

    def make_history(self):
        """
        Makes the history dataframe from the lightcurve dataframe.

        Notes
        -----
        The history is made from the lightcurve data before phase 0.
        Note that DOES include the data that made the object enter the eyeball list.
        So it's really a "first impressions + history" data.

        The dataframe is cropped from the **first historical detection** (we also crop that
        first historical detection). This is to avoid carrying a big dataframe with nothing
        but non detections. We only care about non detections if they're bounded by
        detections ( because they can indicate, how regularly or irregularly something
        pops up in the sky). If it's all non detection, then it's just nothing.

        # TODO: maybe review this. Maybe this is dumb. Because here that means that an object that's
        not been obvserved because it was behind the sun and one with a long history of non detections
        will be treated the same. That might actually be shitty.
        """

        self.history = self.lightcurve[self.lightcurve.phase_init<0]
        self.history['first_mjd'] = self.history[self.history.det == True].mjd.min()
        self.history['last_mjd'] = self.history[self.history.det == True].mjd.max()

        # We also crop all the data before and including the first historical detection
        # that's just how I'm defining these features.
        self.history = self.history[self.history['mjd'] > self.history['first_mjd']]

        # Calculate the cumulative number of detections on our cropped data
        # that does mean that there is one fewer detection than in our initial data
        # since we cropped that first detection above. It's completely fine so long
        # as all the data has its features calculated the same way.
        self.history['N_dets'] = self.history['det'].cumsum()

    def add_dayN_column(self):
        # TODO: add a test
        """
        Adds the dayN column to the lightcurve dataframe
        """
        self.lightcurve = add_dayN_col(self.lightcurve)
        self.detections = add_dayN_col(self.detections)
        self.non_detections = add_dayN_col(self.non_detections)
        if self.history is not None:
            self.history = add_dayN_col(self.history)


class FeaturesSingleSource(object):
    # TODO: try in dev env
    feature_names_day1 = day1_lc_feature_columns + context_feature_columns
    feature_names_dayN = dayN_lc_feature_columns +  feature_names_day1

    def __init__(self, atlas_id, api_config_file):
        #TODO: add docstring (include showing how it's meant to be used
        self.atlas_id = atlas_id
        self.json_data = JsonDataFromServer(atlas_id, api_config_file=api_config_file)

        ## Get the last visit MJD (only needed when doing updates but cheap to compute)
        try:
            last_lc_mjd = self.json_data.get_values(['lc', 'mjd'])[-1]
        except IndexError:
            last_lc_mjd = float('-inf')  # or any other default value

        try:
            last_lcnondets_mjd = self.json_data.get_values(['lcnondets', 'mjd'])[-1]
        except IndexError:
            last_lcnondets_mjd = float('-inf')  # or any other default value

        self.last_visit_mjd = max(last_lc_mjd, last_lcnondets_mjd)

    def make_day1_features(self):
        self.lightcurve_pipes_day1 = LightCurvePipes(self.json_data, phase_bounds=(-100,0))
        self.lightcurve_pipes_day1.add_dayN_column()
        self.day1_lcfeatures = make_day1_lcfeatures(self.lightcurve_pipes_day1)
        self.contextual_features = make_contextual_features(self.json_data)
        self.day1_features = self.day1_lcfeatures + self.contextual_features

    def make_dayN_features(self):
        self.make_day1_features()
        self.lightcurve_pipes_dayN = LightCurvePipes(self.json_data, phase_bounds=(-5, 15))
        self.lightcurve_pipes_dayN.add_dayN_column()
        self.dayN_lcfeatures = make_dayN_lcfeatures(self.lightcurve_pipes_dayN)
        self.dayN_features = self.dayN_lcfeatures + self.day1_features

