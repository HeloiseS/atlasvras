class VRASaysNo(Exception):
    """
    Generic exception to throw when user does something we're not allowing them to do
    because we decided they shouldn't be allowed
    """

class VRAAPIError(Exception):
    """
    Generic exception for when the API craps out
    """

class VRAKeyError(Exception):
    """
    Generic exception for when we can't find a key in a dictionary and it's a st3ph3n specific issue
    """

class VRAWarning(Warning):
    """
    Generic VRAWarning
    """

class LightcurveTimeoutError(Exception):
    def __init__(self, data_url):
        super().__init__(f"Data not available after timeout. Check manually at: {data_url}")
        self.data_url = data_url
