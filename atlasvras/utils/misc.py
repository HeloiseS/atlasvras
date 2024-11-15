import pandas as pd
import atlasapiclient as atlasapi
from atlasvras.utils.exceptions import VRASaysNo

def fetch_vra_dataframe(datethreshold: str = None,
                        API_CONFIG_FILE: str = atlasapi.utils.API_CONFIG_FILE
                        ):
    """
    Convenience function to get the VRA table in a dataframe in one line.
    Instantiates RequestVRAScores and returns the response as a dataframe.

    Parameters
    ----------
    datethreshold : str
        Date in the format "YYYY-MM-DD" to filter the VRA table by date. Will return all dates after.

    API_CONFIG_FILE : str
        Path to the API configuration file.

    Returns
    -------
    vra_df : pandas dataframe
        pandas dataframe containing the VRA table

    Raises
    ------
    VRASaysNo
        If datethreshold is None

    Examples
    --------
    >>> fetch_vra_dataframe(datethreshold='2024-11-14',
                            API_CONFIG_FILE=API_CONFIG_FILE)
    """

    if datethreshold is None:
        raise VRASaysNo("You need to provide a date threshold otherwise it'll take forever")

    request_vra = atlasapi.client.RequestVRAScores(api_config_file=API_CONFIG_FILE,
                                               payload={'datethreshold': datethreshold},
                                               get_response=True
                                                )
    vra_df = pd.DataFrame(request_vra.response)

    return vra_df