class SassConfigurationError(Exception):
    """
    This ERROR should be used when there is a problem with the 
    configuration settings in the settings.py file.
    """
    pass

class SassCommandArgumentError(Exception):
    """
    This ERROR should be used when there is a problem with the 
    arguments being passed in from the command line.
    """
    pass

class SassConfigException(Exception):
    pass