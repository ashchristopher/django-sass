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


class SassGenerationError(Exception):
    """
    This ERROR is used when there was a problem using Sass to
    generate css files. This could be caused by issues with the 
    sass file itself.
    """
    pass


class SassException(Exception):
    pass

class SassConfigException(Exception):
    pass