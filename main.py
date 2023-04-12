import os
import discord
import logging
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
#from discord_slash import SlashCommand

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='+', owner_ids=os.getenv('OWNER_ID'), intents=intents)
#slash = SlashCommand(client, sync_commands=True)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the showroom. | prefix: +"))
    print(f'[INFO] User >> {client.user}\n[INFO] Sign In >> Successful')

#####
# COGS START
#####

async def load():
    for filename in os.listdir('./cogs'):
       	if filename.endswith('.py'):
           	await client.load_extension(f'cogs.{filename[:-3]}')

#####
# COGS END
#####

async def main():
	async with client:
		await load()
		await client.start(TOKEN, reconnect=True)

#client.run(TOKEN, reconnect=True)
asyncio.run(main())
