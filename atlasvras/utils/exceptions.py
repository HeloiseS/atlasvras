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

