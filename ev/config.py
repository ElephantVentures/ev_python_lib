import codecs
import collections
import json
import os

def _merge_dicts(d1, d2):
  """
  Modifies d1 in-place to contain values from d2.  If any value
  in d1 is a dictionary (or dict-like), *and* the corresponding
  value in d2 is also a dictionary, then merge them in-place.
  """
  for k, v2 in d2.items():
    v1 = d1.get(k)
    if isinstance(v1, collections.Mapping) and isinstance(v2, collections.Mapping):
      _merge_dicts(v1, v2)
    else:
      d1[k] = v2

_env_var = 'EV_ENV'
def get_env_varname():
  return _env_var

def set_env_varname(env_var):
  global _env_var
  _env_var = env_var

def get_env():
  return os.environ.get(_env_var, 'dev')

def _load_file(f):
  with codecs.open(f, mode = 'r', encoding = 'utf-8') as in_stream:
    return json.load(in_stream)

class Config(object):
  def __init__(self, *files):
    self.data = _load_file(files[0])
    for f in files[1:]:
      _merge_dicts(self.data, _load_file(f))

_configs = {}
def get_config(env = None, public_file = None, private_file = None):
  env = env or get_env()
  public_file = public_file or 'config_public_{}.json'.format(env)
  private_file = private_file or 'config_private.json'

  key = (public_file, private_file)
  config = _configs.get(key)
  if not config:
    config = Config(*key)
    _configs[key] = config

  return config
