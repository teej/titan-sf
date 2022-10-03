import os

__version__ = "0.0.2"

TITAN_DEFAULT_SCHEMA = "TITAN"
TITAN_PATH = os.path.abspath(os.environ["TITAN_PATH"])
TITAN_LOGO = r"""
    __  _ __          
   / /_(_) /____ ____ 
  / __/ / __/ _ `/ _ \
  \__/_/\__/\_,_/_//_/
   

""".strip(
    "\n"
)

from titan.reserved import RESERVED_FUNCTION_NAMES
