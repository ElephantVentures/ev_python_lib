"""This is the config module.

This allows configuration files to be loaded and interpreted in a simple,
straightforward way. It does this by defining an "environment variable"
(EV_ENV by default) that defines the environment the code is running in, or
"dev" if the environment doesn't exist.

The basic assumption is that there will be two json config files, one public
(named "config_public_<env>.json" and checked in and managed through source
control) and one private (named "config_private.json" and managed outside of
source control, typically stored in a secure location).

In this case, loading the configuration is as simple as ``import config; c =
config.get_config()``. Keys in the private config file will be merged into the
public config file, and returned.

"""

import codecs
from collections import Mapping
import json
import os

# Python 2/3 compatibility
try:
  basestring
except NameError:
  basestring = str

def _merge_dicts(d1, d2):
  """
  Modifies d1 in-place to contain values from d2.  If any value
  in d1 is a dictionary (or dict-like), *and* the corresponding
  value in d2 is also a dictionary, then merge them in-place.

  """
  for k, v2 in d2.items():
    v1 = d1.get(k)
    if isinstance(v1, Mapping) and isinstance(v2, Mapping):
      _merge_dicts(v1, v2)
    else:
      d1[k] = v2

_env_var = 'EV_ENV'
def get_env_varname():
  """Return the global environment variable name. EV_ENV by default."""
  return _env_var

def set_env_varname(env_var):
  """Set the global environment variable name. EV_ENV by default."""
  global _env_var
  _env_var = env_var

def get_env():
  """Return the environment. "dev" if empty or unset."""
  return os.environ.get(_env_var, 'dev')

def _load_file(f):
  with codecs.open(f, mode = 'r', encoding = 'utf-8') as in_stream:
    return json.load(in_stream)

class Config(dict):

  """A mapping class which represents a (json-based) mapping of configuration objects."""

  def __init__(self, *files, **kwargs):
    """If provided with a dictionary or named arguments, populates itself from that
    information.  Otherwise assumes a list of filenames, and loads each provided
    file in turn, merging it (and overriding keys) from the previously loaded
    file. The files are expected to be utf-8 encoded JSON files, each with a
    single JSON object.

    """
    if kwargs or (len(files) == 1 and not isinstance(files[0], basestring)):
      return dict.__init__(self, *files, **kwargs)

    dict.__init__(self) # init with an empty dictionary
    for f in files:
      _merge_dicts(self, _load_file(f))

_configs = {}
def get_config(env = None, public_file = None, private_file = None):
  """Load configuration information from the filesystem.

  In many cases, "config.get_config()" will be all that is necessary. You can
  modify the default behavior in a couple ways.

  If you specify ``env`` it will use that as the environment you're running
  in. If you specify ``public_file`` it will load the public data from that
  file. If you specify ``private_file`` it will load the private data from
  that file.

  """
  env = env or get_env()
  public_file = public_file or 'config_public_{}.json'.format(env)
  private_file = private_file or 'config_private.json'

  key = (public_file, private_file)
  config = _configs.get(key)
  if not config:
    config = Config(*key)
    _configs[key] = config

  return config
