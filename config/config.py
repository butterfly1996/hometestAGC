import os
from dotenv import load_dotenv
from configparser import ConfigParser, BasicInterpolation
load_dotenv()


class EnvInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        return os.path.expandvars(value)


CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) + '/config.ini'
PARSER = ConfigParser(interpolation=EnvInterpolation())
PARSER.read(CONFIG_FILE)


def get_config(section, key):
    return PARSER.get(section, key)