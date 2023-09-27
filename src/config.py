import os

# Fixed value
VERSION = '0.1.2'

# use environment var in os
# required
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
CONOHA_API_TENANT_ID = os.environ.get('CONOHA_API_TENANT_ID')
CONOHA_API_IDENTITY_SERVICE = os.environ.get('CONOHA_API_IDENTITY_SERVICE')
CONOHA_API_USER_NAME = os.environ.get('CONOHA_API_USER_NAME')
CONOHA_API_USER_PASSWORD = os.environ.get('CONOHA_API_USER_PASSWORD')

CONOHA_API_IMAGE_SERVICE = os.environ.get('CONOHA_API_IMAGE_SERVICE')
CONOHA_API_COMPUTE_SERVICE = os.environ.get('CONOHA_API_COMPUTE_SERVICE')
CONOHA_API_NETWORK_SERVICE = os.environ.get('CONOHA_API_NETWORK_SERVICE')
CONOHA_API_VM_PLAN_FLAVOR_UUID = os.environ.get('CONOHA_API_VM_PLAN_FLAVOR_UUID')

# option
VM_AND_IMAGE_NAME = 'asagao-for-minecraft-'+os.environ.get('VM_AND_IMAGE_NAME', '') if os.environ.get('VM_AND_IMAGE_NAME', '') != '' else 'asagao-for-minecraft'
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '')
DISCORD_CHANNEL_NAMES = os.environ.get('DISCORD_CHANNEL_NAMES', 'minecraft, minecraft-test').replace(' ', '').split(',')

# secret
HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME = os.environ.get('HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME', None)
ALLOW_PROCESS_KILL_COMMAND = os.environ.get('ALLOW_PROCESS_KILL_COMMAND', None)

if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME == None:
  HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME = ''

if ALLOW_PROCESS_KILL_COMMAND == 'true':
  ALLOW_PROCESS_KILL_COMMAND = True
else:
  ALLOW_PROCESS_KILL_COMMAND = False
