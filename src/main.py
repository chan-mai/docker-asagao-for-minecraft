import sys
import time
import discord
from discord.ext import tasks, commands
from conoha import conoha_wrap, conoha_main, conoha_sub
import utils.utility as utility
import datetime
from config import *

class Bot(commands.AutoShardedBot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.isProcessing = False
    self.channel = None

intents = discord.Intents.default()
intents.guilds = True
bot = Bot(intents=discord.Intents.all(), debug_guilds=DISCORD_GUILD_IDS)

# 起動時


@bot.event
async def on_ready():
  print('discord login')
  if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME != '':
    bot.channel = discord.utils.get(
        bot.get_all_channels(), name=DISCORD_CHANNEL_NAMES[0]
    )
    sidekiq.start()


# 定期的に実行したいfunction
if HOUR_FOR_IMAGE_LEAVE_ALONE_LONG_TIME != '':
  @tasks.loop(minutes=60)
  async def sidekiq():
    if datetime.datetime.now().strftime('%H') == '19-9':
      is_should_open_and_close = await conoha_wrap.is_should_open_and_close(bot.channel)
      if is_should_open_and_close:
        await utility.post_embed_failed(bot.channel, f"expiration date warninig:\n\
          <@{ADMIN_USER_ID}>\n\
          It's been 30 days since last created the Image.\n\
          Please run this command:\n\
          > {utility.full_commands('open_and_close')}")


async def open_vm(_channel):
  if bot.isProcessing:
    await utility.post_embed_failed(_channel, f"You can only run one at a time.\nCanceled: {utility.full_commands('open')}")
    return None
  bot.isProcessing = True
  await conoha_main.create_vm_from_image(_channel)
  bot.isProcessing = False


async def close_vm(_channel):
  if bot.isProcessing:
    await utility.post_embed_failed(_channel, f"You can only run one at a time.\nCanceled: {utility.full_commands('close')}")
    return None
  bot.isProcessing = True
  await conoha_main.create_image_from_vm(_channel)
  bot.isProcessing = False


def check_channel_name(_channel_name):
  if _channel_name in DISCORD_CHANNEL_NAMES:
    return True
  else:
    return False


# Minecraftサーバー起動コマンド
@bot.slash_command(
    name="open",
    description="Create VM from image, for play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
async def open(ctx: discord.ApplicationContext):
  interaction = ctx.interaction
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
@bot.slash_command(
    name="close",
    description="Delete VM and save image, finished play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
async def close(ctx: discord.ApplicationContext):
  interaction = ctx.interaction
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
@bot.slash_command(
    name="help",
    description="help.",
    guilds=DISCORD_GUILD_IDS
)
async def help(ctx: discord.ApplicationContext):
  interaction = ctx.interaction
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  print('help')
  embed = await utility.create_help_embed()
  await interaction.response.send_message(embed=embed)

# conoha vm plansコマンド
@bot.slash_command(
    name="plan",
    description="ConoHa vm plans list.",
    guilds=DISCORD_GUILD_IDS
)
async def plan(ctx: discord.ApplicationContext):
  interaction = ctx.interaction
  if check_channel_name(interaction.channel.name) == False:
    await interaction.response.send_message(
        'This command is not available in this channel.',
        ephemeral=True,
    )
    return None
  await interaction.response.defer()
  print('plan')

  embed = await conoha_sub.create_conoha_vm_plans_embed(interaction.channel)
  await interaction.followup.send(embed=embed)

# open_and_closeコマンド
@client.tree.command(
    name="open_and_close",
    description="Create VM from image, for play minecraft.\nDelete VM and save image, finished play minecraft.",
    guilds=DISCORD_GUILD_IDS
)
@discord.app_commands.guilds(*DISCORD_GUILD_IDS)
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


bot.run(DISCORD_TOKEN)
