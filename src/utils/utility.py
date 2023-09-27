import discord
import json
from config import *
import utils.logger_wrap as logger_wrap

logger = logger_wrap.logger(__name__)


def parse_json(_json):
  _json = json.loads(_json)
  _json = json.dumps(_json, indent=2)
  print(_json)
  return _json


async def post_message(_channel: discord.TextChannel,  _content):
  await _channel.send(_content)
  logger.info(_content)


async def post_embed(_channel: discord.TextChannel, _title='', _content='', _color=discord.Color.default):
  embed = discord.Embed(title=_title, description=_content, color=_color)
  await _channel.send(embed=embed)


async def create_embed_complite(_title: str, _content: str):
  _content = _content + '\ndone.'
  embed = discord.Embed(title=_title, description=_content, color=discord.Color.green())
  logger.info(f'post_embed_complite\n\
    {_title}\n\
    {_content}')
  return embed


async def create_embed_failed(_content: str):
  _content = _content + f'\nPlease try again or contact admin user, or confirm command.\n<@{ADMIN_USER_ID}>'
  embed = discord.Embed(title='Failed', description=_content, color=discord.Color.gold())
  logger.warning(f'post_embed_failed\n\
    Failed\n\
    {_content}')
  return embed


async def post_embed_complite(_channel: discord.TextChannel, _title, _content):
  _content = _content + '\ndone.'
  await post_embed(_channel, _title=_title, _content=_content, _color=discord.Color.green())
  logger.info(f'post_embed_complite\n\
    {_title}\n\
    {_content}')


async def post_embed_failed(_channel: discord.TextChannel, _content):
  _content = _content + f'\nPlease try again or contact admin user, or confirm command.\n<@{ADMIN_USER_ID}>'
  await post_embed(_channel, _title='Failed', _content=_content, _color=discord.Color.gold())
  logger.warning(f'post_embed_failed\n\
    Failed\n\
    {_content}')


async def post_embed_error(_channel: discord.TextChannel, _content):
  _content = _content + f'\n\
    Stop asagao-minecraft server.\n\
    Can not run all commands.\n\
    Please contact admin user.\n\
    <@{ADMIN_USER_ID}>'
  await post_embed(_channel, _title='Error', _content=_content, _color=discord.Color.red())
  logger.error(f'post_embed_error\n\
    Error\n\
    {_content}')


async def post_user_id(_message: discord.Message):
  channel = _message.channel
  await post_embed_complite(channel, 'user id', str(_message.author.id))


async def post_version(_channel):
  content = f"\
    > {VERSION}\n\
  "
  await post_embed_complite(_channel, 'asagao-for-minecraft version', content)


async def create_help_embed():
  content = "\
    > Create VM from image, for play minecraft.\n\
    > /open\n\
    \n\
    > Delete VM and save image, finished play minecraft.\n\
    > /close\n\
    \n\
    > help.\n\
    > /help\n\
    \n\
    > ConoHa vm plans list.\n\
    > /plan\n\
    \n\
    > user id.\n\
    > /myid\n\
    \n\
    > this app version.\n\
    > /version\n\
    \n\
  "
  return discord.Embed(title='asagao-for-minecraft help', description=content, color=discord.Color.green())
