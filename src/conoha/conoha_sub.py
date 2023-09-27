import requests
import json
import conoha_wrap
import utils.utility as utility
from config import *


async def post_discord_conoha_vm_plans(_channel):
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token == None:
    return None
  headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
  try:
    response = requests.get(CONOHA_API_COMPUTE_SERVICE+'/flavors', headers=headers)
    if response.status_code == 200:
      flavors = json.loads(response.text)['flavors']
      flavors = '\n'.join([f"> name: {f['name']}\n> id: {f['id']}\n" for f in flavors])
      await utility.post_embed_complite(_channel, 'conoha vm plans', flavors)
    else:
      await utility.post_embed_failed(_channel, f'get CONOHA_API_COMPUTE_SERVICE/flavors: {response.status_code}.')
      return None
  except requests.exceptions.RequestException as e:
    await utility.post_embed_failed(_channel, f'get CONOHA_API_COMPUTE_SERVICE/flavors: RequestException.')
    return None
