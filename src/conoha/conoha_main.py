import time
import requests
import json
import conoha.conoha_wrap as conoha_wrap
import utils.utility as utility
from config import *
import utils.logger_wrap as logger_wrap

logger = logger_wrap.logger(__name__)


async def create_vm_from_image(_channel):
  await utility.post_message(_channel, '> minecraft world opening...')
  # サーバーのVMが存在しているとき実行しない
  await utility.post_message(_channel, '> checking...')
  servers = await conoha_wrap.get_servers_for_minecraft(_channel)
  if servers == None:
    await utility.post_embed_failed(_channel, 'Could not get VM data.\nPlease try again.')
    return None
  if len(servers) != 0:
    await utility.post_embed_failed(_channel, 'Exist VM already.')
    return None

  # imageを取得して、存在しなかったら実行しない
  images = await conoha_wrap.get_images(_channel)
  if images == None:
    await utility.post_embed_failed(_channel, 'Could not get image.\nPlease try again.')
    return None
  if len(images) == 0:
    await utility.post_embed_failed(_channel, 'Not Exist Image.')
    return None
  image = images[0]
  image_status = await conoha_wrap.get_image_status(_channel, image)
  if image_status == None:
    return None
  if image_status != 'ACTIVE':
    await utility.post_embed_failed(_channel, 'Image is not Active.')
    return None

  # VMを作成
  await utility.post_message(_channel, '> Start create VM.')
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token == None:
    return None
  headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
  data = {
    'server': {
      'imageRef': image['id'],
      'flavorRef': CONOHA_API_VM_PLAN_FLAVOR_UUID,
      'security_groups': [
        {
          'name': 'default'
        },
        {
          'name': 'gncs-ipv4-all'
        }
      ],
      'metadata': {
        'instance_name_tag': VM_AND_IMAGE_NAME
      }
    }
  }
  try:
    response = requests.post(CONOHA_API_COMPUTE_SERVICE+'/servers', data=json.dumps(data), headers=headers)
    response_json = response.json()
    key = next(iter(response_json))
    if response.status_code == 202:
      await utility.post_message(_channel, '> Success: Create VM.')
    else:
      await utility.post_embed_failed(_channel, f'get CONOHA_API_COMPUTE_SERVICE/servers: {response.status_code}\nsmessage: {response_json[key]["message"]}.')
      return None
  except requests.exceptions.RequestException as e:
    await utility.post_embed_failed(_channel, 'get CONOHA_API_COMPUTE_SERVICE/servers: RequestException.')
    return None

  # VMの起動(Build)が完了するまで待機
  await utility.post_message(_channel, '> VM building...')
  wait_time_first = 100
  wait_every_time = 10
  time.sleep(wait_time_first)
  server_status = ''
  number_of_trials = 20
  servers = []
  for i in range(number_of_trials):
    servers = await conoha_wrap.get_servers_for_minecraft(_channel)
    if servers != None:
      if len(servers) == 0:
        await utility.post_message(_channel, '> Failed: VM create failed, server vm is not exist.')
        return None
      server_status = servers[0]['status']
      if server_status == 'ACTIVE':
        await utility.post_message(_channel, f'> Done. VM build time = {str(wait_time_first+i*wait_every_time)}(s).')
        break
    if i == number_of_trials-1:
      await utility.post_embed_failed(_channel, 'VM create failed.\nserver_status is not ACTIVE.')
      return None
    time.sleep(wait_every_time)

  # ipAddress取得
  server_addresses = servers[0]['addresses']
  ip_address = ''
  for display_nic_key in server_addresses: # ex: "ext-133-130-48-0-xxx"
    adresses_ip4_and_ip6 = server_addresses[display_nic_key]
    for address in adresses_ip4_and_ip6:
      if address['version'] == 4:
        ip_address = address['addr']
  if ip_address == '':
    await utility.post_embed_failed(_channel, 'Could not get ip address.')
    return None

  # imageを削除
  await utility.post_message(_channel, '> Start remove used image.')
  exist_vm_and_image = await conoha_wrap.exist_both_vm_and_image(_channel)
  if exist_vm_and_image != True:
    return None
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token == None:
    return None
  headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
  wait_time_first = 0
  wait_every_time = 10
  time.sleep(wait_time_first)
  number_of_trials = 5
  for i in range(number_of_trials):
    try:
      response = requests.delete(CONOHA_API_IMAGE_SERVICE+'/v2/images/'+image['id'], headers=headers)
      if response.status_code == 204:
        await utility.post_message(_channel, f'> Success: image is deleted.')
        break
      else:
        await utility.post_message(_channel, f"> [{i}/{number_of_trials}] delete CONOHA_API_IMAGE_SERVICE/v2/images/[image['id']]: {str(response.status_code)}\n\
          > False: Could not remove image.")
      time.sleep(wait_every_time)
    except requests.exceptions.RequestException as e:
      await utility.post_embed_failed(_channel, "delete CONOHA_API_IMAGE_SERVICE/v2/images/[image['id']]: RequestException.")
    if i == number_of_trials-1:
      return None

  # ip address表示
  await utility.post_embed_complite(_channel, 
        'Hello Minecraft World!', 
        f'ip address: **{ip_address}**')

  # image削除完了を待つ
  # await utility.post_message(_channel, '> Removing image...')
  wait_time_first = 5
  wait_every_time = 5
  number_of_trials = 15
  for i in range(number_of_trials):
    images = await conoha_wrap.get_images(_channel)
    if images != None:
      if len(images) == 0:
        # await utility.post_message(_channel, f'> Removed image done. \n\
        #                               > Removed image time = {str(wait_time_first+i*wait_every_time)}(s).')
        break
    if i == number_of_trials-1:
      await utility.post_embed_failed(_channel, 'Could not remove image.')
      return None
    time.sleep(wait_every_time)

  # await utility.post_embed_complite(_channel, 
  #   'complete create vm.', 
  #   'no problem')


async def create_image_from_vm(_channel):
  await utility.post_message(_channel, '> minecraft world closing...')
  # imageが存在しているとき、VMの準備ができてない時は実行しない
  await utility.post_message(_channel, '> checking...')
  images = await conoha_wrap.get_images(_channel)
  if images == None:
    await utility.post_embed_failed(_channel, 'Could not get image info.\nPlease try again.')
    return None
  if len(images) >= 1:
    await utility.post_embed_failed(_channel, 'Image is already exist.')
    return None

  # VMを取得して、VMが取得できなかったら実行しない
  servers = await conoha_wrap.get_servers_for_minecraft(_channel)
  if servers == None:
    await utility.post_embed_failed(_channel, 'Could not get VM.')
    return None
  if len(servers) == 0:
    await utility.post_embed_failed(_channel, 'VM shutdown failed, because server not exist.')
    return None
  server = servers[0]
  server_id = server['id']

  # VMを停止する
  if server['status'] != 'SHUTOFF':
    conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
    if conoha_api_token == None:
      return None
    headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
    data = {
      'os-stop': None
    }
    try:
      response = requests.post(CONOHA_API_COMPUTE_SERVICE+'/servers/'+server_id+'/action', data=json.dumps(data), headers=headers)
      if response.status_code == 202:
        await utility.post_message(_channel, '> Success: stopped VM.')
      else:
        await utility.post_message(_channel, f'> post CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: {str(response.status_code)}\n\
          > False: Could not stop.')
        return None
    except requests.exceptions.RequestException as e:
      await utility.post_message(_channel, f'> post CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: RequestException')
      return None

  # VMのシャットダウンが完了するまで待機
  wait_time_first = 2
  wait_every_time = 5
  time.sleep(wait_time_first)
  server_status = ''
  for i in range(10):
    servers = await conoha_wrap.get_servers_for_minecraft(_channel)
    if servers != None:
      if len(servers) == 0:
        await utility.post_message(_channel, '> Failed: VM shutdown failed, because server not exist.')
        return None
      server_status = servers[0]['status']
      if server_status == 'SHUTOFF':
        await utility.post_message(_channel, f'> Done. VM shutdown time = {str(wait_time_first+i*wait_every_time)}(s).')
        break
    time.sleep(wait_every_time)
  if server_status != 'SHUTOFF':
    await utility.post_message(_channel, '> VM shutdown failed.')
    return None

  # イメージを作成する
  await utility.post_message(_channel, '> Start create Image...')
  wait_time_first = 0
  wait_every_time = 5
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token == None:
    return None
  headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
  data = {
    'createImage': {
      'name': VM_AND_IMAGE_NAME
    }
  }
  try:
    number_of_trials = 3
    for i in range(number_of_trials):
      response = requests.post(CONOHA_API_COMPUTE_SERVICE+'/servers/'+server_id+'/action', data=json.dumps(data), headers=headers)
      if response.status_code == 202:
        await utility.post_message(_channel, '> Success: create Image.')
        break
      else:
        await utility.post_message(_channel, f'[{i}/{number_of_trials}] post CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: {response.status_code}.')
      if i == number_of_trials-1:
        return None
      time.sleep(wait_every_time)
  except requests.exceptions.RequestException as e:
    await utility.post_embed_failed(_channel, 'post CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: RequestException.')
    return None

  # Image作成完了まで待機
  await utility.post_message(_channel, '> Creating Image...')
  wait_time_first = 70
  wait_every_time = 20
  time.sleep(wait_time_first)
  number_of_trials = 20
  for i in range(number_of_trials):
    exist_vm_and_image = await conoha_wrap.exist_both_vm_and_image(_channel)
    if exist_vm_and_image:
      await utility.post_message(_channel, f'> Done.Create image time = {str(wait_time_first+i*wait_every_time)}(s).')
      break
    if i == number_of_trials-1:
      utility.post_embed_failed(_channel, 'Could not finish create image.')
      return None
    time.sleep(wait_every_time)

  # VM削除
  await utility.post_message(_channel, '> Start remove VM...')
  exist_vm_and_image = await conoha_wrap.exist_both_vm_and_image(_channel)
  if exist_vm_and_image != True:
    return None
  wait_time_first = 0
  wait_every_time = 10
  conoha_api_token = await conoha_wrap.get_conoha_api_token(_channel)
  if conoha_api_token == None:
    return None
  headers = {'Accept': 'application/json', 'X-Auth-Token': conoha_api_token}
  try:
    number_of_trials = 5
    for i in range(number_of_trials):
      response = requests.delete(CONOHA_API_COMPUTE_SERVICE+'/servers/'+server_id, headers=headers)
      if response.status_code == 204:
        await utility.post_message(_channel, '> Success: Remove VM.')
        break
      else:
        await utility.post_embed_failed(_channel, f'[{i+1}/{number_of_trials}]delete CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: {response.status_code}.')
      if i == number_of_trials-1:
        return None
      time.sleep(wait_every_time)
  except requests.exceptions.RequestException as e:
    await utility.post_embed_failed(_channel, 'delete CONOHA_API_COMPUTE_SERVICE/servers/[server_id]: RequestException.')
    return None

  # VM削除完了を待つ
  await utility.post_message(_channel, '> Removing VM...')
  wait_time_first = 5
  wait_every_time = 10
  number_of_trials = 15
  for i in range(number_of_trials):
    servers = await conoha_wrap.get_servers_for_minecraft(_channel)
    if servers == None:
      continue
    if len(servers) == 0:
      await utility.post_message(_channel, f'> Done. Removed VM time = {str(wait_time_first+i*wait_every_time)}(s).')
      break
    if i == number_of_trials-1:
      await utility.post_embed_failed(_channel, 'Could not remove VM.')
      return None
    time.sleep(wait_every_time)

  await utility.post_embed_complite(_channel, 
    'complete remove vm.', 
    'no problem.Thank you!')
