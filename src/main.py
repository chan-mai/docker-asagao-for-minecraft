import sys
import time
from typing import Any
import discord
from discord import app_commands
from discord.ext import tasks
from discord.flags import Intents
from conoha import conoha_wrap, conoha_main, conoha_sub
import utils.utility as utility
import datetime
from config import *


class Client(discord.Client):
  def __init__(self, *, intents: Intents, **options: Any) -> None:
    super().__init__(intents=intents, **options)
    self.isProcessing: bool = False
    self.channel = None
    # SlashCommand用にコマンドツリーを定義
    self.tree = app_commands.CommandTree(self)


client = Client(intents=discord.Intents.all())

# 起動時


@client.event
async def on_ready():
  print('discord login')
  if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME != '':
    client.channel = discord.utils.get(
        client.get_all_channels(), name=DISCORD_CHANNEL_NAMES[0]
    )
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


def check_channel_name(_channel_name):
  if _channel_name in DISCORD_CHANNEL_NAMES:
    return True
  else:
    return False


# Minecraftサーバー起動コマンド
@client.tree.add_command(
    name="open",
    description="Create VM from image, for play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def open(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  await interaction.response.send_message('starting open vm...')
  print('open')
  await open_vm(interaction.channel)


# Minecraftサーバー停止コマンド
@client.tree.add_command(
    name="close",
    description="Delete VM and save image, finished play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def close(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  await interaction.response.send_message('starting close vm...')
  print('close')
  await close_vm(interaction.channel)


# helpコマンド
@client.tree.add_command(
    name="help",
    description="help.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def help(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('help')
  await utility.post_asagao_minecraft_commands(interaction.channel)


# conoha vm plansコマンド
@client.tree.add_command(
    name="plan",
    description="ConoHa vm plans list.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def plan(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('plan')
  await conoha_sub.post_discord_conoha_vm_plans(interaction.channel)


# myidコマンド
@client.tree.add_command(
    name="myid",
    description="user id.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def myid(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('myid')
  await utility.post_user_id(interaction)


# versionコマンド
@client.tree.add_command(
    name="version",
    description="asagao-for-minecraft version.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def version(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('version')
  await utility.post_version(interaction.channel)


# open_and_closeコマンド
@client.tree.add_command(
    name="open_and_close",
    description="Create VM from image, for play minecraft.\nDelete VM and save image, finished play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guild_only()
async def open_and_close(interaction: discord.Interaction):
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('open_and_close')
  await open_vm(interaction.channel)
  time.sleep(10)
  await close_vm(interaction.channel)


client.run(DISCORD_TOKEN)
