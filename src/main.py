# python3 -m pip install -U discord.py
# pip install requests

import sys
import time
import discord
from discord.ext import tasks
import requests
import json
import conoha_wrap
import conoha_main
import conoha_sub
import utility
import datetime
from config import *


client = discord.Client(intents=discord.Intents.all())
client.isProcessing = False
client.channel = None

# 起動時
@client.event
async def on_ready():
  print('discord login')
  if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME != '':
    client.channel = discord.utils.get(client.get_all_channels(), name=DISCORD_CHANNEL_NAMES[0])
    sidekiq.start()


# 定期的に実行したいfunction
if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME != '':
  @tasks.loop(minutes=60)
  async def sidekiq():
    if datetime.datetime.now().strftime('%H') == '19-9':
      is_should_open_and_close = await conoha_wrap.is_should_open_and_close(client.channel)
      if is_should_open_and_close:
        await utility.post_embed_failed(client.channel, f"expiration date warninig:\n\
          <@{ADMIN_USER_ID}>\n\
          It's been 30 days since last created the Image.\n\
          Please run this command:\n\
          > {utility.full_commands('open_and_close')}")


async def open_vm(_channel):
  if client.isProcessing:
    await utility.post_embed_failed(_channel, f"You can only run one at a time.\nCanceled: {utility.full_commands('open')}")
    return None
  client.isProcessing = True
  await conoha_main.create_vm_from_image(_channel)
  client.isProcessing = False


async def close_vm(_channel):
  if client.isProcessing:
    await utility.post_embed_failed(_channel, f"You can only run one at a time.\nCanceled: {utility.full_commands('close')}")
    return None
  client.isProcessing = True
  await conoha_main.create_image_from_vm(_channel)
  client.isProcessing = False


# メッセージ受信時
@client.event
async def on_message(_message):
  if _message.author.bot or not(_message.channel.name in DISCORD_CHANNEL_NAMES):
    return

  channel = _message.channel

  if _message.content in utility.full_commands('open'):
    await open_vm(channel)

  if _message.content in utility.full_commands('close'):
    await close_vm(channel)

  if _message.content in utility.full_commands('help'):
    await utility.post_asagao_minecraft_commands(channel)

  if _message.content in utility.full_commands('plan'):
    await conoha_sub.post_discord_conoha_vm_plans(channel)

  if _message.content in utility.full_commands(['myid', 'userid']):
    await utility.post_user_id(_message)

  if _message.content in utility.full_commands('version'):
    await utility.post_version(channel)

  if _message.content in utility.full_commands('open_and_close'):
    await open_vm(channel)
    time.sleep(10)
    await close_vm(channel)

  if ALLOW_PROCESS_KILL_COMMAND:
    if _message.content in utility.full_commands('exit'):
      await utility.post_embed_complite(channel, 'exit', 'python process is finished.')
      sys.exit()

client.run(DISCORD_TOKEN)
