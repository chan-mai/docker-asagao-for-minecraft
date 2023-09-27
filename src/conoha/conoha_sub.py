import requests
import json
import conoha.conoha_wrap as conoha_wrap
import utils.utility as utility
from config import *


async def create_conoha_vm_plans_embed(_channel):
  embed = await utility.create_embed_failed('conoha vm plans failed.')
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token != None:
    headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
    try:
      response = requests.get(CONOHA_API_COMPUTE_SERVICE+'/flavors', headers=headers)
      if response.status_code == 200:
        flavors = json.loads(response.text)['flavors']
        flavors = '\n'.join([f"> name: {f['name']}\n> id: {f['id']}\n" for f in flavors])
        embed = await utility.create_embed_complite('conoha vm plans', flavors)
      else:
        embed = await utility.create_embed_failed(f'get CONOHA_API_COMPUTE_SERVICE/flavors: {response.status_code}.')
    except requests.exceptions.RequestException as e:
      embed = await utility.create_embed_failed(_channel, f'get CONOHA_API_COMPUTE_SERVICE/flavors: RequestException.')
  return embed
